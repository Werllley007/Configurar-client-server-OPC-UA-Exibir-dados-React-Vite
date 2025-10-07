# Configuração do React-Vite


## 1. Instalação do Node.js

Para começar com o React, você precisa ter o Node.js instalado. Ele é necessário para o React e para o comando npx.

**Baixe o Instalador**: Vá para o site oficial do Node.js:

```bash
https://nodejs.org/
```

**Recomendação**: Baixe a versão LTS (Long-Term Support - Suporte de Longo Prazo), que é a mais estável e recomendada para a maioria dos usuários.

**Instalação**: Execute o instalador baixado. Mantenha as configurações padrão. É crucial que a opção "Add to PATH" esteja marcada, mas geralmente ela já vem marcada por padrão.

## 2. Verificação da Instalação
Após a instalação, abra um novo terminal (ou Prompt de Comando/PowerShell) e execute os seguintes comandos para verificar se tudo está funcionando:

```bash
node -v
npm -v
```

## 3. Criando o Projeto React
Agora que o npx está disponível, você pode tentar criar o projeto novamente.

Volte para a pasta C:\Users\Desktop no seu terminal e execute:

```bash
npx create-react-app meu-projeto-opcua-web
```

Quando terminar, entre na pasta do projeto e inicie o servidor de desenvolvimento:

```bash
cd meu-projeto-opcua-web
npm start
```

## 4. Como usar o VS Code

Depois que o Node.js estiver instalado, você pode usar o Terminal Integrado do VS Code, que é a maneira mais prática de criar e gerenciar seu projeto.

Abra o VS Code.

Vá em **Terminal** no menu superior e clique em **Novo Terminal** (ou use o atalho: Ctrl + ' no Windows).

Neste terminal que se abrirá dentro do VS Code, você pode finalmente executar os comandos para **criar seu projeto React/Vite**, pois ele reconhecerá o npm que você instalou:

### 1. Verifique se o Node/npm está funcionando no terminal do VS Code
```bash
node -v
npm -v
```
### 2. Crie seu projeto React usando Vite

O Vite se tornou a maneira mais rápida e moderna de iniciar um projeto React. Ele oferece uma experiência de desenvolvimento super-rápida, utilizando a capacidade nativa de módulos ES do navegador.

Abra seu terminal e execute o seguinte comando:

```bash
npm create vite@latest
```
Ou pode usar o comando abaixo para inserir o nome do projeto e o tipo de template usado que no caso é o REACT

```bash
npm create vite@latest meu-projeto-opcua-web -- --template react
```
### 3. Entre na pasta do projeto
```bash
cd meu-projeto-opcua-web
```
### 4. Instale as dependências (as bibliotecas necessárias)
```bash
npm install
```
### 5. Inicie o servidor de desenvolvimento
```bash
npm run dev
```













