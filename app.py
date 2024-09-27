from flask import Flask, render_template, request, redirect, url_for
import datetime
from ics import Calendar, Event
import smtplib

app = Flask(__name__)

# Vaccination Relevance Info
vaccination_relevance = {
    "BCG, OPV, Hepatitis B": "These vaccines protect against tuberculosis (BCG), polio (OPV), and hepatitis B.",
    "Pentavalent 1, OPV 1, PCV 1, RV 1": "These protect against diphtheria, tetanus, whooping cough, hepatitis B, Hib, polio, pneumococcal infections, and rotavirus.",
    "Pentavalent 2, OPV 2, PCV 2, RV 2": "Follow-up doses to strengthen the child's immunity.",
    "Pentavalent 3, OPV 3, PCV 3, IPV": "Further doses for continued protection against infectious diseases.",
    "Measles, Yellow Fever, Men A": "These vaccines protect against measles, yellow fever, and meningitis."
}

# Function to calculate vaccination schedule
def calculate_vaccination_schedule(dob):
    vaccinations = {
        "BCG, OPV, Hepatitis B": 0,
        "Pentavalent 1, OPV 1, PCV 1, RV 1": 6,
        "Pentavalent 2, OPV 2, PCV 2, RV 2": 10,
        "Pentavalent 3, OPV 3, PCV 3, IPV": 14,
        "Measles, Yellow Fever, Men A": 36,
    }
    schedule = {}
    for vaccine, weeks in vaccinations.items():
        vaccination_date = dob + datetime.timedelta(weeks=weeks)
        schedule[vaccine] = vaccination_date
    return schedule

# Function to send email with calendar invite
def send_email_with_calendar(mother_email, child_name, schedule):
    c = Calendar()
    for vaccine, date in schedule.items():
        e = Event()
        e.name = f'{vaccine} for {child_name}'
        e.begin = date.strftime('%Y-%m-%d')
        e.description = f'This is a vaccination reminder for {vaccine}'
        c.events.add(e)

    # Save calendar file
    with open(f"{child_name}_vaccination_schedule.ics", 'w') as f:
        f.writelines(c)

    # Send email (replace with your email and credentials)
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        subject = f"{child_name}'s Vaccination Schedule"
        body = "Please find attached the vaccination schedule for your child."
        msg = f'Subject: {subject}\n\n{body}'
        
        # Send the email
        server.sendmail(sender_email, mother_email, msg)

    print("Email sent successfully!")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    child_name = request.form['child_name']
    dob_input = request.form['dob']
    dob = datetime.datetime.strptime(dob_input, '%Y-%m-%d')
    mother_mobile = request.form['mother_mobile']
    mother_email = request.form['mother_email']

    schedule = calculate_vaccination_schedule(dob)

    return render_template(
        'schedule.html', 
        child_name=child_name, 
        schedule=schedule, 
        vaccination_relevance=vaccination_relevance
    )

@app.route('/send_email', methods=['POST'])
def send_email():
    child_name = request.form['child_name']
    mother_email = request.form['mother_email']
    dob_input = request.form['dob']
    dob = datetime.datetime.strptime(dob_input, '%Y-%m-%d')

    schedule = calculate_vaccination_schedule(dob)
    send_email_with_calendar(mother_email, child_name, schedule)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
