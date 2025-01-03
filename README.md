# Create ENV first #
py -m venv clonetest

# Activate ENV #
clonetest\Scripts\activate

# Firststep Use comands #
pip install -r requirements.txt

# load data commands #  
python manage.py load_mockup_data

# make sure you already create new enc for this #
# don't forget to swift cd #

