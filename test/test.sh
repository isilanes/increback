# Run tests and then show coverage report (only if no errors):
coverage run --source="." -m unittest discover -s test -v && coverage report -m --skip-covered --omit=test/README
