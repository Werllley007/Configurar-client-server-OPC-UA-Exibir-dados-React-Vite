# Configurar client/server OPC UA & Exibir dados em uma aplicação front-end em React com Vite

Neste projeto é criada uma **aplicação front-end em React com Vite** para exibir os dados do **cliente OPC UA** que recebe esses dados do **server OPC UA**.

Para isso, adiciona-se uma **camada intermediária**: um pequeno servidor Web em Python (Flask ou FastAPI). Isso porque o React (que roda no navegador) não consegue se conectar diretamente a um servidor OPC UA. Ele precisa de uma API HTTP para solicitar os dados.


## Instalação do Node.js

Para começar com o React, você precisa ter o Node.js instalado. Ele é necessário para o React e para o comando npx.

**Baixe o Instalador**: Vá para o site oficial do Node.js:

```bash
https://nodejs.org/
```

**Recomendação**: Baixe a versão LTS (Long-Term Support - Suporte de Longo Prazo), que é a mais estável e recomendada para a maioria dos usuários.

**Instalação**: Execute o instalador baixado. Mantenha as configurações padrão. É crucial que a opção "Add to PATH" esteja marcada, mas geralmente ela já vem marcada por padrão.

## Verificando se o node esta configurado no VS Code

Abra o terminal no VS Code, você pode finalmente executar os comandos para **criar seu projeto React/Vite**, pois ele reconhecerá o npm que você instalou:

Abra o terminal no VS code e execute
```bash
node -v
npm -v
```









### Crie seu projeto React usando Vite

O Vite se tornou a maneira mais rápida e moderna de iniciar um projeto React. Ele oferece uma experiência de desenvolvimento rápida, utilizando a capacidade nativa de módulos ES do navegador.

Abra seu terminal e execute o seguinte comando:

```bash
npm create vite@latest
```
Ou pode usar o comando abaixo para inserir o nome do projeto e o tipo de template usado que no caso é o REACT

```bash
npm create vite@latest meu-projeto-opcua-web -- --template react
```
### Entre na pasta do projeto
```bash
cd meu-projeto-opcua-web
```
### Instale as dependências (as bibliotecas necessárias)
```bash
npm install
```
### Inicie o servidor de desenvolvimento
```bash
npm run dev
```








# Procedimento para UM e DOIS SERVIDORES OPC-UA 

Sugestão de fazer primeiro para um servidor e depois para dois servidores.

-----------------------------

## UM SERVIDOR OPC-UA 

Crie um novo arquivo chamado **web_api.py**:

```bash
nano web_api.py
```

codigo: [web_api.py](/um_servidor/web_api.py)

----------------------------

### Criar e Ativar o Ambiente Virtual

Instalar o Flask para o servidor web e o ambiente virtual (flask_env), escolha o nome para o qualquer o seu ambiente no lugar de flask_env.

```bash
sudo apt update
sudo apt install python3-pip python3-venv -y

# 1. Cria e ativa o ambiente virtual
python3 -m venv flask_env
source flask_env/bin/activate

# 2. Instala o Flask
pip install Flask
```

Após a ativação, você verá (flask_env) no início da sua linha de comando, indicando que está no ambiente isolado

### Instalar as dependências do web_api.py:
Com o **ambiente virtual ativo**, instale as dependências. Isso garantirá que o **uvicorn** e os outros pacotes sejam instalados no local correto, onde o ambiente virtual os encontra facilmente.

```bash
pip install fastapi uvicorn freeopcua
```

### Para executar o web_api.py:

```bash
uvicorn web_api:app --reload --port 8000
```

## Crie a Aplicação React (Vite)

### Abra um novo terminal e execute:

```bash
npm create vite@latest vite-opcua-dashboard -- --template react

cd vite-opcua-dashboard

npm install
```
------------------------------------------------------------

### Caso seja com UM SERVIDOR OPC-UA Edite src/App.jsx:

Substitua o conteúdo de meu-projeto-opcua-web/src/App.jsx pelo seguinte:

```bash
cd meu-projeto-opcua-web/src/
nano App.jsx
```

codigo: [App.jsx](/um_servidor/App.jsx)

------------------------------------------------------------

###  Edite src/App.css:

Substitua o conteúdo de meu-projeto-opcua-web/src/App.css pelo seguinte:

```bash
cd meu-projeto-opcua-web/src/
nano App.css
```
codigo: [App.css](/um_servidor/App.css)


## Execute a Aplicação React

No terminal do projeto vite-opcua-dashboard, execute:

**Terminal 1**: Execute o servidor OPC UA (corrigido).

Windows:
```bash
python.exe opcua_server.py
```

Linux:
```bash
python opcua_server.py
```

**Terminal 2**: Execute o servidor Web FastAPI para **um Servidor**.

Windows:
```bash
python.exe -m venv venv

.\venv\Scripts\Activate

uvicorn web_api:app --reload --port 8000
```

Linux:
```bash
python -m venv venv

source venv/bin/activate

uvicorn web_api:app --reload --port 8000
```

**Terminal 2**: Execute o servidor Web FastAPI para **dois Servidor**.

Windows:
```bash
python.exe -m venv venv

.\venv\Scripts\Activate

uvicorn web_api_new:app --reload --port 8000
```

Linux:
```bash
python3 -m venv flask_env
source flask_env/bin/activate

uvicorn web_api_new:app --reload --port 8000

**Terminal 3**: No diretório vite-opcua-dashboard, execute a aplicação React.

Dentro da pasta (Windows ou Linux):

```bash
cd vite-opcua-dashboard

npm run dev
```

O Vite iniciará o servidor de desenvolvimento e te dará um link (geralmente **http://localhost:5173**). Abra este link no seu navegador.

Você deverá ver um dashboard simples em React exibindo os valores dos sensores de temperatura, tempo de atividade e produção total, atualizando-se a cada 3 segundos.



-----------------------------

## DOIS SERVIDORES OPC-UA 

Crie um novo arquivo chamado **web_api_new.py**:

```bash
nano web_api_new.py
```

codigo: [web_api_new.py](/dois_servidores/web_api_new.py)



### DOIS SERVIDORES OPC-UA Edite src/App.jsx:

Substitua o conteúdo de meu-projeto-opcua-web/src/App.jsx pelo seguinte:

```bash
cd meu-projeto-opcua-web/src/
nano App.jsx
```
codigo: [App_new.jsx](/dois_servidores/App.jsx)



###  Edite src/App.css:

Substitua o conteúdo de meu-projeto-opcua-web/src/App.css pelo seguinte:

```bash
cd meu-projeto-opcua-web/src/
nano App.css
```
codigo: [App.css](/um_servidor/App.css)



