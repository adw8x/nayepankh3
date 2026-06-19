import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, Response
from sqlalchemy import or_
from datetime import datetime
from reports import generate_full_report, generate_volunteer_report, generate_beneficiary_report
import csv
import io

from models import db, Volunteer, Beneficiary, Program, ActivityLog

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-local-dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///nayepankh.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'exports'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()

# === MAIN ROUTES ===

@app.route('/')
def dashboard():
    total_volunteers = Volunteer.query.count()
    total_beneficiaries = Beneficiary.query.count()
    active_programs = Program.query.filter_by(status='Active').count()
    cities_covered = len(set([city for (city,) in db.session.query(Volunteer.city).distinct().all()] + [city for (city,) in db.session.query(Beneficiary.city).distinct().all()]))
    
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()

    return render_template('dashboard.html', 
                           total_volunteers=total_volunteers,
                           total_beneficiaries=total_beneficiaries,
                           active_programs=active_programs,
                           cities_covered=cities_covered,
                           recent_activities=recent_activities,
                           active_page='dashboard')

@app.route('/api/chart-data')
def chart_data():
    # Beneficiaries per program
    beneficiaries_per_program = db.session.query(Program.name, db.func.count(Beneficiary.id)).join(Beneficiary).group_by(Program.name).all()
    program_labels = [row[0] for row in beneficiaries_per_program]
    program_data = [row[1] for row in beneficiaries_per_program]

    # Volunteers by city
    volunteers_by_city = db.session.query(Volunteer.city, db.func.count(Volunteer.id)).group_by(Volunteer.city).all()
    city_labels = [row[0] for row in volunteers_by_city]
    city_data = [row[1] for row in volunteers_by_city]

    return jsonify({
        'beneficiariesPerProgram': {'labels': program_labels, 'data': program_data},
        'volunteersByCity': {'labels': city_labels, 'data': city_data}
    })

# === VOLUNTEER ROUTES ===

@app.route('/volunteers')
def volunteers():
    page = request.args.get('page', 1, type=int)
    query = Volunteer.query

    # Search
    q = request.args.get('q')
    if q:
        query = query.filter(or_(
            Volunteer.name.ilike(f'%{q}%'),
            Volunteer.email.ilike(f'%{q}%'),
            Volunteer.city.ilike(f'%{q}%')
        ))

    # Filter
    status = request.args.get('status')
    if status:
        query = query.filter(Volunteer.status == status)
    
    city = request.args.get('city')
    if city:
        query = query.filter(Volunteer.city == city)

    # Sort
    sort = request.args.get('sort', 'joined_date')
    order = request.args.get('order', 'desc')
    if hasattr(Volunteer, sort):
        if order == 'asc':
            query = query.order_by(getattr(Volunteer, sort).asc())
        else:
            query = query.order_by(getattr(Volunteer, sort).desc())

    volunteers_paginated = query.paginate(page=page, per_page=10, error_out=False)
    
    # For filter dropdowns
    cities = db.session.query(Volunteer.city).distinct().order_by(Volunteer.city).all()
    programs = Program.query.order_by(Program.name).all()

    return render_template('volunteers.html', 
                           volunteers=volunteers_paginated,
                           cities=[c[0] for c in cities],
                           programs=programs,
                           current_q=q,
                           current_status=status,
                           current_city=city,
                           current_program=request.args.get('program', ''),
                           current_sort=sort,
                           current_order=order,
                           active_page='volunteers')

@app.route('/volunteers/add', methods=['GET', 'POST'])
def add_volunteer():
    programs = Program.query.all()
    if request.method == 'POST':
        try:
            new_volunteer = Volunteer(
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                city=request.form['city'],
                age=int(request.form['age']),
                gender=request.form['gender'],
                profession=request.form['profession'],
                skills=request.form['skills'],
                programs_interested=','.join(request.form.getlist('programs_interested')),
                availability_days=','.join(request.form.getlist('availability_days')),
                hours_per_week=int(request.form['hours_per_week']),
                mode=request.form['mode'],
                why_volunteer=request.form['why_volunteer']
            )
            db.session.add(new_volunteer)
            db.session.flush() # To get the ID for the log
            log = ActivityLog(entity_type='Volunteer', entity_id=new_volunteer.id, action='Added', details=f"Volunteer {new_volunteer.name} was added.")
            db.session.add(log)
            db.session.commit()
            flash('Volunteer added successfully!', 'success')
            return redirect(url_for('volunteers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding volunteer: {e}', 'danger')
    return render_template('volunteer_form.html', programs=programs, form_action='add')

@app.route('/volunteers/<int:id>')
def volunteer_detail(id):
    volunteer = Volunteer.query.get_or_404(id)
    return render_template('volunteer_detail.html', volunteer=volunteer)

@app.route('/volunteers/<int:id>/edit', methods=['GET', 'POST'])
def edit_volunteer(id):
    volunteer = Volunteer.query.get_or_404(id)
    programs = Program.query.all()
    if request.method == 'POST':
        try:
            volunteer.name = request.form['name']
            volunteer.email = request.form['email']
            volunteer.phone = request.form['phone']
            volunteer.city = request.form['city']
            volunteer.age = int(request.form['age'])
            volunteer.gender = request.form['gender']
            volunteer.profession = request.form['profession']
            volunteer.skills = request.form['skills']
            volunteer.programs_interested = ','.join(request.form.getlist('programs_interested'))
            volunteer.availability_days = ','.join(request.form.getlist('availability_days'))
            volunteer.hours_per_week = int(request.form['hours_per_week'])
            volunteer.mode = request.form['mode']
            volunteer.why_volunteer = request.form['why_volunteer']
            volunteer.status = request.form['status']
            volunteer.hours_contributed = int(request.form['hours_contributed'])
            
            log = ActivityLog(entity_type='Volunteer', entity_id=volunteer.id, action='Updated', details=f"Volunteer {volunteer.name} details were updated.")
            db.session.add(log)
            db.session.commit()
            flash('Volunteer updated successfully!', 'success')
            return redirect(url_for('volunteer_detail', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating volunteer: {e}', 'danger')
    return render_template('volunteer_form.html', volunteer=volunteer, programs=programs, form_action='edit')

@app.route('/volunteers/<int:id>/delete', methods=['POST'])
def delete_volunteer(id):
    volunteer = Volunteer.query.get_or_404(id)
    try:
        log = ActivityLog(entity_type='Volunteer', entity_id=id, action='Deleted', details=f"Volunteer {volunteer.name} was deleted.")
        db.session.add(log)
        db.session.delete(volunteer)
        db.session.commit()
        flash('Volunteer deleted successfully.', 'success')
        return redirect(url_for('volunteers'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting volunteer: {e}', 'danger')
        return redirect(url_for('volunteers'))

@app.route('/volunteers/export')
def export_volunteers():
    volunteers = Volunteer.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'City', 'Age', 'Gender', 'Profession', 'Skills', 'Programs Interested', 'Availability', 'Hours/Week', 'Mode', 'Status', 'Joined Date', 'Hours Contributed'])
    
    # Data
    for v in volunteers:
        writer.writerow([v.id, v.name, v.email, v.phone, v.city, v.age, v.gender, v.profession, v.skills, v.programs_interested, v.availability_days, v.hours_per_week, v.mode, v.status, v.joined_date.strftime('%Y-%m-%d'), v.hours_contributed])
    
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=volunteers.csv"})

# === BENEFICIARY ROUTES ===

@app.route('/beneficiaries')
def beneficiaries():
    query = Beneficiary.query
    program_id = request.args.get('program_id')
    if program_id:
        query = query.filter_by(program_id=program_id)
    status = request.args.get('status')
    if status:
        query = query.filter(Beneficiary.status == status)
    
    beneficiaries = query.all()
    programs = Program.query.order_by(Program.name).all()
    return render_template('beneficiaries.html', beneficiaries=beneficiaries, programs=programs, current_program=program_id, current_status=status or '', active_page='beneficiaries')

@app.route('/beneficiaries/add', methods=['GET', 'POST'])
def add_beneficiary():
    programs = Program.query.all()
    if request.method == 'POST':
        try:
            new_beneficiary = Beneficiary(
                name=request.form['name'],
                age=int(request.form['age']),
                gender=request.form['gender'],
                city=request.form['city'],
                school_name=request.form.get('school_name'),
                program_id=int(request.form['program_id']),
                enrollment_date=datetime.strptime(request.form['enrollment_date'], '%Y-%m-%d'),
                parent_name=request.form['parent_name'],
                parent_phone=request.form['parent_phone'],
                notes=request.form.get('notes')
            )
            db.session.add(new_beneficiary)
            db.session.flush()
            log = ActivityLog(entity_type='Beneficiary', entity_id=new_beneficiary.id, action='Added', details=f"Beneficiary {new_beneficiary.name} was added.")
            db.session.add(log)
            db.session.commit()
            flash('Beneficiary added successfully!', 'success')
            return redirect(url_for('beneficiaries'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding beneficiary: {e}', 'danger')
    return render_template('beneficiary_form.html', programs=programs, form_action='add')

@app.route('/beneficiaries/<int:id>/edit', methods=['GET', 'POST'])
def edit_beneficiary(id):
    beneficiary = Beneficiary.query.get_or_404(id)
    programs = Program.query.all()
    if request.method == 'POST':
        try:
            beneficiary.name = request.form['name']
            beneficiary.age = int(request.form['age'])
            beneficiary.gender = request.form['gender']
            beneficiary.city = request.form['city']
            beneficiary.school_name = request.form.get('school_name')
            beneficiary.program_id = int(request.form['program_id'])
            beneficiary.enrollment_date = datetime.strptime(request.form['enrollment_date'], '%Y-%m-%d')
            beneficiary.status = request.form['status']
            beneficiary.parent_name = request.form['parent_name']
            beneficiary.parent_phone = request.form['parent_phone']
            beneficiary.performance_score = int(request.form['performance_score']) if request.form.get('performance_score') else None
            beneficiary.notes = request.form.get('notes')
            
            log = ActivityLog(entity_type='Beneficiary', entity_id=beneficiary.id, action='Updated', details=f"Beneficiary {beneficiary.name} details were updated.")
            db.session.add(log)
            db.session.commit()
            flash('Beneficiary updated successfully!', 'success')
            return redirect(url_for('beneficiaries'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating beneficiary: {e}', 'danger')
    return render_template('beneficiary_form.html', beneficiary=beneficiary, programs=programs, form_action='edit')

@app.route('/beneficiaries/<int:id>/delete', methods=['POST'])
def delete_beneficiary(id):
    beneficiary = Beneficiary.query.get_or_404(id)
    try:
        log = ActivityLog(entity_type='Beneficiary', entity_id=id, action='Deleted', details=f"Beneficiary {beneficiary.name} was deleted.")
        db.session.add(log)
        db.session.delete(beneficiary)
        db.session.commit()
        flash('Beneficiary deleted successfully.', 'success')
        return redirect(url_for('beneficiaries'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting beneficiary: {e}', 'danger')
        return redirect(url_for('beneficiaries'))

# === PROGRAM ROUTES ===

@app.route('/programs')
def programs():
    programs = db.session.query(
        Program, 
        db.func.count(Beneficiary.id).label('enrolled_count')
    ).outerjoin(Beneficiary, Program.id == Beneficiary.program_id).group_by(Program.id).all()
    return render_template('programs.html', programs=programs, active_page='programs')

# === SEARCH ROUTE ===

@app.route('/search')
def search():
    q = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    city = request.args.get('city', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    results = {'volunteers': [], 'beneficiaries': [], 'programs': []}
    total_results = 0

    if q:
        # Search Volunteers
        if search_type in ['all', 'volunteer']:
            v_query = Volunteer.query.filter(or_(
                Volunteer.name.ilike(f'%{q}%'),
                Volunteer.email.ilike(f'%{q}%'),
                Volunteer.skills.ilike(f'%{q}%')
            ))
            if city: v_query = v_query.filter(Volunteer.city.ilike(f'%{city}%'))
            if status: v_query = v_query.filter(Volunteer.status == status)
            results['volunteers'] = v_query.all()
            total_results += len(results['volunteers'])

        # Search Beneficiaries
        if search_type in ['all', 'beneficiary']:
            b_query = Beneficiary.query.filter(or_(
                Beneficiary.name.ilike(f'%{q}%'),
                Beneficiary.parent_name.ilike(f'%{q}%')
            ))
            if city: b_query = b_query.filter(Beneficiary.city.ilike(f'%{city}%'))
            if status: b_query = b_query.filter(Beneficiary.status == status)
            results['beneficiaries'] = b_query.all()
            total_results += len(results['beneficiaries'])

        # Search Programs
        if search_type in ['all', 'program']:
            p_query = Program.query.filter(or_(
                Program.name.ilike(f'%{q}%'),
                Program.description.ilike(f'%{q}%')
            ))
            if city: p_query = p_query.filter(Program.city.ilike(f'%{city}%'))
            if status: p_query = p_query.filter(Program.status == status)
            results['programs'] = p_query.all()
            total_results += len(results['programs'])

    cities = [row[0] for row in db.session.query(Volunteer.city).distinct().order_by(Volunteer.city).all()]
    pages = max(1, (total_results + 9) // 10)
    return render_template('search.html', 
                           results=results, 
                           total_results=total_results,
                           q=q, 
                           search_type=search_type, 
                           city=city, 
                           status=status,
                           page=page,
                           pages=pages,
                           cities=cities,
                           active_page='search')

# === REPORT ROUTES ===

@app.route('/reports')
def reports():
    return render_template('reports.html', active_page='reports')

@app.route('/reports/generate', methods=['POST'])
def generate_report():
    report_type = request.form.get('report_type')
    filename = None
    try:
        if report_type == 'full':
            volunteers = Volunteer.query.all()
            beneficiaries = Beneficiary.query.all()
            programs = Program.query.all()
            filename = generate_full_report(volunteers, beneficiaries, programs)
        elif report_type == 'volunteers':
            volunteers = Volunteer.query.filter_by(status='Active').all()
            filename = generate_volunteer_report(volunteers)
        elif report_type == 'beneficiaries':
            beneficiaries = Beneficiary.query.all()
            filename = generate_beneficiary_report(beneficiaries)
        
        if filename:
            flash(f'Report "{filename}" generated successfully!', 'success')
            return redirect(url_for('download_report', filename=filename))
        else:
            flash('Could not generate report. Invalid report type.', 'danger')
            return redirect(url_for('reports'))
    except Exception as e:
        flash(f'An error occurred while generating the report: {e}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/download/<filename>')
def download_report(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000)