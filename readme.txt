
pip install -r requirements.txt

rm db.sqlite3
rm -rf migrations
python manage.py makemigrations storyboard
python manage.py migrate
python manage.py shell
from storyboard import views
views.startup()
exit()

python manage.py runserver



