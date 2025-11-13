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

# Procedimento para UM e DOIS SERVIDORES OPC-UA 

Sugestão de desenvolvimento, siga o tutorial para um servidor e depois para dois servidores.

-----------------------------

## UM SERVIDOR OPC-UA 

Crie um novo arquivo chamado **web_api.py**:

```bash
nano web_api.py
```

codigo: [web_api.py](/um_servidor/web_api.py)

----------------------------

### Criar e Ativar o Ambiente Virtual

Instalar o Flask para o servidor web e o ambiente virtual (test_venv), escolha o nome para o qualquer o seu ambiente no lugar de test_venv.

```bash
sudo apt update
sudo apt install python3-pip python3-venv -y

# 1. Cria e ativa o ambiente virtual
python3 -m venv test_venv
source test_venv/bin/activate
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
**Observação**: Caso apresente erro acima troque 8000 por 8001.


## Crie a Aplicação React (Vite)

O Vite se tornou a maneira mais rápida e moderna de iniciar um projeto React. Ele oferece uma experiência de desenvolvimento rápida, utilizando a capacidade nativa de módulos ES do navegador.

### Abra um novo terminal e execute:

```bash
npm create vite@latest vite-opcua-dashboard -- --template react

Use rolldown-vite (Experimental)?:
│  ○ Yes
│  ● No

Install with npm and start now?
│  ● Yes / ○ No
```

Se chegou aqui é porque não teve erros até o momento.

```bash
  VITE v7.2.2  ready in 178 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

Pressione Ctrl + c para sair da tela acima, depois entre na pasta do projeto.

```bash
cd vite-opcua-dashboard

npm install
```

### Edite vite-opcua-dashboard/src/App.jsx:

Substitua o conteúdo de vite-opcua-dashboard/src/App.jsx:

```bash
cd vite-opcua-dashboard/src/
nano App.jsx
```
pelo seguinte:

codigo: [App.jsx](/um_servidor/App.jsx)


###  Edite vite-opcua-dashboard/src/App.css:

Substitua o conteúdo de meu-projeto-opcua-web/src/App.css:

```bash
cd vite-opcua-dashboard/src/
nano App.css
```
pelo seguinte:

codigo: [App.css](/um_servidor/App.css)

###  Criando opcua_client.py:

Crie um novo arquivo chamado **opcua_client.py**:

```bash
nano opcua_client.py
```
codigo: [opcua_client.py](/opcua_client.py)


###  Criando opcua_server.py:

Crie um novo arquivo chamado **opcua_server.py**:

```bash
nano opcua_server.py
```

codigo: [opcua_server.py](/opcua_server.py)


## Execute a Aplicação React

No terminal do projeto vite-opcua-dashboard, execute:

**Terminal 1**: Execute o servidor OPC UA (corrigido).

Windows:
```bash
python.exe opcua_server.py
```
Ou

Linux:
```bash
python3 opcua_server.py
```
**Terminal 2**: Execute o servidor Web FastAPI para **um Servidor**.

Windows:
```bash
# 1. Cria e ativa o ambiente virtual
python.exe -m venv venv
.\venv\Scripts\Activate

uvicorn web_api:app --reload --port 8000
```

Ou

Linux:
```bash
# 1. Cria e ativa o ambiente virtual
python3 -m venv test_venv
source test_venv/bin/activate

uvicorn web_api:app --reload --port 8000
```

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

###  Criando **web_api_new.py**:

Crie um novo arquivo chamado **web_api_new.py**:

```bash
nano web_api_new.py
```
codigo: [web_api_new.py](/dois_servidores/web_api_new.py)

###  Criando **opcua_server_new.py**:

Crie um novo arquivo chamado **opcua_server_new.py**:

```bash
nano opcua_server_new.py
```
codigo: [opcua_server_new.py](/dois_servidores/opcua_server_new.py)

### Edite vite-opcua-dashboard/src/App.jsx:

Substitua o conteúdo de meu-projeto-opcua-web/src/App.jsx pelo seguinte:

```bash
cd vite-opcua-dashboard/src/
nano App.jsx
```
codigo: [App.jsx](/dois_servidores/App.jsx)



###  Edite vite-opcua-dashboard/src/App.css:

Substitua o conteúdo de meu-projeto-opcua-web/src/App.css pelo seguinte:

```bash
cd vite-opcua-dashboard/src/
nano App.css
```
codigo: [App.css](/dois_servidores/App.css)


## Execute a Aplicação React

No terminal do projeto vite-opcua-dashboard, execute:

**Terminal 1**: Execute o servidor 1 OPC UA.

Windows:
```bash
python.exe opcua_server.py
```
Ou

Linux:
```bash
python3 opcua_server.py
```

codigo: [opcua_server.py](/dois_servidores/opcua_server.py)

**Terminal 2**: Execute o servidor 2 OPC UA.

Windows:
```bash
python.exe opcua_server_new.py
```
Ou

Linux:
```bash
python3 opcua_server_new.py
```
codigo: [opcua_server_new.py](/dois_servidores/opcua_server_new.py)

**Terminal 3**: Execute o servidor Web FastAPI **web_api_new.py**.

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
```

codigo: [web_api_new.py](/dois_servidores/web_api_new.py)

**Terminal 3**: No diretório vite-opcua-dashboard, execute a aplicação React.

Tanto para Windows ou Linux, dentro da pasta vite-opcua-dashboard:

```bash
cd vite-opcua-dashboard

npm run dev
```

