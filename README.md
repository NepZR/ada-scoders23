<img align="right" src="https://ada-site-frontend.s3.sa-east-1.amazonaws.com/home/header-logo.svg" style="width: 96px;" alt="Ada Tech Logo" />

## Sistema de Monitoramento de Avanços no Campo da Genômica

> This project is related to the fourth module of the Data Engineering Track, Data Extraction I, of Ada Tech's Program in collaboration with Santander, named Santander Coders 2023. The purpose of this repository is to centralize all development of the Monitoring System proposed as the Final Project for this Module, made with ❤️ by <a href="https://github.com/NepZR">Lucas Rodrigues (@NepZR)</a>.

---

## 🚀 How to Run:
> Disclaimer: this project was developed using **Python 3.10** as a base version and using Docker Compose. If you have a Previous Python Version or Docker is not installed, upgrade/install is needed. Otherwise, **the project will not be debuggable/executable**.

### 1. Clone the repository

~~~shell
git clone git@github.com:NepZR/ada-scoders23.git -b "data-extraction-module"
~~~

### 2. Access the Project Folder
~~~shell
cd ada-scoders23/
~~~

### 3. Start the Docker Compose for this project
~~~shell
docker-compose up -d --build
~~~
> Depending on how you installed Docker, the initial command can be `docker-compose` or `docker compose`.

---

## 🌍 API - Webhook
> 🎮 Demo the Webhook API running the Python Notebook `api_demo.ipynb` located in the root folder of this project.


#### - Host and Port: `http://localhost:6000`
#### - Endpoints available: `/search` [POST]
<br>

#### - Payload Type: `json`
#### - JSON Data:
- `keywords`: `List[str]` containing the keywords for the search;
- `since_hours`: `int` with the number of hours since the moment of request to be used as the search range. By default, it is set as `1`.
- `language`: `str` with the 2-letter ISO-639-1 code of the desired language. Accepted values: `en`, `br`.
<br><br>

#### - Example Request:
~~~python
import requests

json_payload = {
  "keywords": ["dna", "genomic", "customized medicine"],
  "since_hours": 24,
  "language": "en"
}
response = requests.post(url="http://localhost:6000", json=json_payload)
if response.status_code == 200:
    print(response.json())
~~~

#### - Example Response - `JSON` with `HTTP 200`:
~~~json
{
  "status": "No results found. Search Range: NOW-24h",
  "keywords": ["dna", "genomic", "customized medicine"],
  "search_result": null
}
~~~
> When results are found, they will be in the `search_result` key as a `List[dict]` and the `status` key will contain the number of results found.

---

<h2 style="text-align: justify;">
  ⚙️ About the developer
</h2>

<table style="display: flex; align-itens: center; justify-content: center;">
  <tr>
    <td align="center"><a href="https://github.com/NepZR"><img style="width: 150px; height: 150;" src="https://avatars.githubusercontent.com/u/37887926" width="100px;" alt=""/><br /><sub><b>Lucas Rodrigues</b></sub></a><br /><sub><b>Data Engineer | Python Developer</sub></a></td>
  </tr>
<table>

---

###### Last Updated: 2023-10-01 (Sunday). Author: Lucas Rodrigues (@NepZR | lucas.darlindo@gmail.com).