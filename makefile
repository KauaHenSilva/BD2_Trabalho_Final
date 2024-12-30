all:
# services:
#   postgres:
#     image: postgres:16-alpine
#     restart: always
#     environment:
#       POSTGRES_USER: root
#       POSTGRES_PASSWORD: root
#       POSTGRES_DB: database-postgres
#     ports:
#       - "5432:5432"
	# sudo docker run --network host --name postgres -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root -e POSTGRES_DB=Database_BD2 -p 5432:5432 -d postgres:16-alpine
	sudo docker build -t script_bd_2 .
	sudo docker run --network host script_bd_2
