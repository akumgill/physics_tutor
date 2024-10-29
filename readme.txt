
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py shell
from storyboard import views
views.startup()
views.import_questions()
exit()

python manage.py runserver



