# Fictional Pancake App
The project is available online:
www.fictionalpancake.herokuapp.com

With the recent focus on various news outlets and filter bubbles, we wanted to see if an algorithm can classify comments on news sites.

Our tool WriteLike returns the predicted class of a comment using Naive Bayes, SGD or Perceptron. It will predict New York Times, Breitbart News, Mother Jones, or Media Matters.

### Thanks
We'd like thank our parents and the following, all of which were
essential:
- Django
- Scikit-learn
- Pandas
- Numpy
- django-extentions, django-rq, pytz
- Textblob and NLTK
- APIs for access: NTY Community and Disqus

### How it works
We collect comments from NYT and Disqus APIs via the modules get_nyt_comments and get_disqus_comments. The comments get cleaned
via comment.py and stored in the postgres DB via write_comment.py. Comments are stored in table data_comment, author information is stored in data_author, and forum information is stored in data_forum.
Both, get_nyt_comments and get_disqus_comments, run via scheduled Heroku jobs, but can be started manually via:
`python manage.py runscript get_nyt_comments --script-args $NYT1`

Every day, we train a HashingVectorizer and the three ML models on our comments. This is done via choose_model.py. In order to avoid blocking the web worker, we leverage a Redis queue as specified in worker.py. Therefore, the module choose_model_background.py is being used for these jobs. The best trained model gets stored in the DB so that it can be used for classification of user input. Accuracy on the test set is stored in DB table data_Accuracy for every model.

The website leverages the module predict_class_user_input to classify user input after retrieving HashingVectorizer and best ML model from the DB table data_ModelStorage.

### How the Frontend works
  - In `/ficionalpancake/urls.py` you'll see our main url points to index.html, which is in `data/templates`.
  - This index.html template inherits from base.html, which is where our assets and stylesheets are imported.
  - You'll find all relevant static files in `data/static/` You'll find the Javascript file, predict.js, here. This is the JS for our AJAX form submission.
  - This AJAX request POSTS to the /predict/ url
  - In `data/views.py` you'll see how the PredictFormBaseView loads our form from `data/forms.py` and creates a response after classifying the comment.
  This is accomplished by an AJAX request and a simple JSONMixin (read more here: https://docs.djangoproject.com/en/1.10/topics/class-based-views/mixins/).
  - Back in `predict.js` the response from the form view is used to manipulate the DOM in index.html. This is how we can dynamically show content.

### Local App Setup

Part A: Database
(If you are a heroku collaborator, you may pull down our database)
https://devcenter.heroku.com/articles/heroku-postgres-import-export

1) Make sure postgres is installed on your machine
  - we use 9.5 and this app: https://postgresapp.com/

2) Create a database fictionalpancake with an admin user
  `$ createdb fictionalpancake`
  `$ psql`
  `# CREATE ROLE admin WITH LOGIN PASSWORD 'password';`
  `# GRANT ALL PRIVILEGES ON DATABASE fictionalpancake TO admin;`
  Your DATABASE_URL for this would be
  `postgres://admin:password@localhost/fictionalpancake`

3) `python manage.py makemigrations`
    - this should do nothing, but it is part 1 of syncing databases.

4) python manage.py migrate
  - If there is an error, "image not found", specify a fallback library for
    your local instance of the app
    For Anaconda installations of python:
    `$ export DYLD_FALLBACK_LIBRARY_PATH=$HOME/anaconda3/lib/:$DYLD_FALLBACK_LIBRARY_PATH`
  - You get an error saying the admin user can't log in, give it those privileges explicitly
    `# ALTER ROLE "admin" WITH LOGIN;`

Part B: Environment Variables and Config
1) Clone the repo
2) cd into repo and run: `pip3 install -r requirements.txt`
3) Add to your .env file:
    - API Keys for Disqus and NYT
    - Redis
    - Database url (I have a fallback to the above database)

4) Fire it up!
  `python manage.py runserver`

5) Run jobs with runscript to add comments to the database
  `python manage.py runscript get_nyt_comments --script-args $NYT1`
