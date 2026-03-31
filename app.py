from flask import Flask,render_template,flash,redirect,url_for,session
from flask_sqlalchemy  import SQLAlchemy
from datetime import datetime
from forms import RegistrationForm,LoginForm
from werkzeug.security import check_password_hash,generate_password_hash
import pickle
from preprocess import processing_text
from flask import request
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from sklearn.metrics import confusion_matrix
app = Flask(__name__)


model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))
y_test = pickle.load(open("model/y_test.pkl", "rb"))
y_pred = pickle.load(open("model/y_pred.pkl", "rb"))

app.config['SECRET_KEY']='6fd4b4e26e11b0390f140036895629fe'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'

db=SQLAlchemy(app)


class User(db.Model):
    
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20), unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(150),nullable=False)
    date_created = db.Column( db.DateTime, nullable=False,default=datetime.utcnow)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


@app.route('/')
def home():
    return render_template("home.html",title="home")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()

    
    if form.validate_on_submit():
        # ✅ YAHAN PE CHECK KARNA HAI KI USER PEHLE SE MOJUD HAI YA NAHI
        
        # Check if email already exists
        existing_user_email = User.query.filter_by(email=form.email.data).first()
        if existing_user_email:
            flash('That email is already registered. Please login.', 'danger')
            return redirect(url_for('login'))

        # Check if username already exists
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        if existing_user_username:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )

        db.session.add(user)
        db.session.commit()

        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
   form=LoginForm()
   if form.validate_on_submit():
       user=User.query.filter_by(email=form.email.data).first()
       if user and check_password_hash(user.password, form.password.data):
           session['username'] = user.username 
           flash('You Have been Logged in!','success')
           return redirect(url_for('dashboard'))
       else:
           flash('Login Unsuccessful!.Please check username and password','danger')
   return render_template('login.html',title='Login',form=form)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    confidence = None
    error = None

    if request.method == 'POST':
        review = request.form.get('review')

        if not review or review.strip() == "":
            error = "Please enter a review."

        else:
            processed_review = processing_text(review)

            
            if len(processed_review.split()) < 5:
                error = "Please enter a meaningful review (at least 5 words)."

            else:
                review_vec = vectorizer.transform([processed_review])
                pred = model.predict(review_vec)
                prob = model.predict_proba(review_vec)

                confidence = round(max(prob[0]) * 100, 2)

                if pred[0] == 1:
                    prediction = "Fake Review ❌"
                else:
                    prediction = "Genuine Review ✅"

    return render_template(
        "predict.html",
        prediction=prediction,
        confidence=confidence,
        error=error
    )

@app.route("/confusion-matrix")
def confusion_matrix_view():

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(4,4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Genuine", "Fake"],
        yticklabels=["Genuine", "Fake"]
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    plt.close()
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template(
        "confusion_matrix.html",
        plot_url=plot_url
    )

@app.route("/model_performance")
def model_performance():
    accuracy = 0.88
    precision = 0.87
    recall = 0.89

    return render_template(
        "model_performance.html",
        accuracy=accuracy,
        precision=precision,
        recall=recall
    )


@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    session.clear()  
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form.get('email')
        new_password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            # new password hash karo
            hashed_password = generate_password_hash(new_password)

            user.password = hashed_password
            db.session.commit()

            flash('Password updated successfully! Please login.', 'success')
            return redirect(url_for('login'))

        else:
            flash('Email not found!', 'danger')

    return render_template('forgot_password.html')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)