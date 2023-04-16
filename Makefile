DFCLR=\033[39m
ORANGECLR=\033[93m

# - - - - - - - - - - - - - - - - -
# Push commit to git repo
# - - - - - - - - - - - - - - - - -
git:
	git add .
	git commit -m "$(COMMIT)"
	git push
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Deploy
# - - - - - - - - - - - - - - - - -
reupload: shutdown upload

upload: up-serve up

up-serve:
	cd accessor && make db-d && make up-d
up:
	cd deploy && sudo docker-compose up -d --build

shutdown: shut down-serve down

down-serve:
	cd accessor && make shut && make shutdown && make down
shut:
	sudo docker stop tg_asker
down:
	cd deploy && sudo docker-compose down
# - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - -
# Testing
# - - - - - - - - - - - - - - - - -
db-test:
	python3 bot_test.py
# - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - -
# Code Metrics
# - - - - - - - - - - - - - - - - -
code-metrics:
	echo "\n$(ORANGECLR)Static Data$(DFCLR)" && \
		radon raw ./ && \
	echo "\n$(ORANGECLR)Cyclomatic complexity$(DFCLR)" && \
		radon cc ./ && \
	echo "\n$(ORANGECLR)Halsted Metrics$(DFCLR)" && \
		radon hal ./ && \
	echo "\n$(ORANGECLR)Code maintainability index$(DFCLR)" && \
		radon mi ./
# - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - -
# Code Linter
# - - - - - - - - - - - - - - - - -
lint:
	pylint bot.py logger cases
# - - - - - - - - - - - - - - - - -

