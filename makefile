run_bd:
	sudo docker run --network host --name postgres -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root -e POSTGRES_DB=Database_BD2 -p 5432:5432 -d postgres:16-alpine

run_script:
	sudo docker build -t script_bd_2 .
	sudo docker run --network host script_bd_2