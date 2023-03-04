
# - - - - - - - - - - - - - - - - -
# Push commit to git repo
# - - - - - - - - - - - - - - - - -
git:
	git add .
	git commit -m "$(COMMIT)"
	git push
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Testing
# - - - - - - - - - - - - - - - - -
db-test:
	python3 bot_test.py
# - - - - - - - - - - - - - - - - -

