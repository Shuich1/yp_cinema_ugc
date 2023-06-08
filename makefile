PROJECT_NAME = ETL

all:
	@echo "make start - Запуск контейнеров."
	@echo "make stop - Выключение контейнера."
	@echo "make createsuperuser - Создание суперпользователя."
	@echo "make async_tests - Запуск тестов асинхронного сервиса."
	@echo "make auth_tests - Запуск тестов сервиса авторизации."
	@echo "make research_db - Запуск исследования СУБД"
start:
	docker-compose -f docker-compose.yml -f mongo.docker-compose.yml up -d --build
stop:
	docker-compose -f docker-compose.yml -f mongo.docker-compose.yml down
createsuperuser:
	docker-compose exec django python manage.py createsuperuser
async_tests:
	docker-compose -f fastapi-solution/tests/functional/docker-compose.yml up --build --abort-on-container-exit
	docker-compose -f fastapi-solution/tests/functional/docker-compose.yml down
auth_tests:
	docker-compose -f auth-solution/tests/functional/docker-compose.yml up --build --abort-on-container-exit
	docker-compose -f auth-solution/tests/functional/docker-compose.yml down
research_db:
	cd research \
	&& docker-compose up -d --build \
	&& docker logs -f test_stand \
	&& docker-compose down -v
init_mongo_cluster:
	docker exec mongo_cfg_n1 sh -c "mongosh < /opt/initdb/rs_cfg.js" \
	&& docker exec mongo_s1_n1 sh -c "mongosh < /opt/initdb/rs_s1.js" \
	&& docker exec mongo_s2_n1 sh -c "mongosh < /opt/initdb/rs_s2.js" \
	&& sleep 30 \
	&& docker exec mongo_r1 sh -c "mongosh < /opt/initdb/sc.js" \
	&& docker exec mongo_r1 sh -c "mongosh < /opt/initdb/sh.js"
