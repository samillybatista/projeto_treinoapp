### Versão Alternativa (com Código Ajustado)

Aqui você encontrará exemplos de aplicações Python que utilizam a API [Polar Open AccessLink]. Com o [Polar Open AccessLink], você pode acessar dados diversos registrados em dispositivos Polar.

## Pré-requisitos

* Conta no [Polar Flow](https://flow.polar.com)
* [Python 3](https://www.python.org/downloads/) instalado
* [PIP (Instalador de pacotes Python)](https://pip.pypa.io/en/stable/installation/) instalado

## Introdução

O cliente da API AccessLink é necessário para acessar as APIs. Abaixo, estão descritos os passos para criar o cliente e acessar os dados. Para mais detalhes, consulte a [seção de autenticação](https://www.polar.com/accesslink-api/#authentication) da documentação oficial.

### 1. Criar um novo cliente de API

Acesse https://admin.polaraccesslink.com. Faça login com sua conta do Polar Flow e crie um novo cliente de API.

Quando solicitado, use `http://localhost:5000/oauth2_callback` como URL de redirecionamento de autorização para este exemplo. **É importante usar o URL correto para o redirecionamento** para que as aplicações de exemplo funcionem adequadamente.

Você pode editar o seu cliente de API posteriormente para modificar ou adicionar novos URLs de redirecionamento. Apenas certifique-se de que o URL correto esteja configurado como padrão para estes exemplos.

### 2. Configurar credenciais do cliente

Preencha seu `client_id` e `client_secret` no arquivo [config.yml] (exemplo abaixo):

```bash
client_id: 57a715f8-b7e8-11e7-abc4-cec278b6b50a
client_secret: 62c54f4a-b7e8-11e7-abc4-cec278b6b50a
```

### 3. Instalar dependências do Python

```bash
pip3 install -r requirements.txt
```

## Exemplo de aplicação web

A aplicação web é a forma mais rápida e simples de começar. Ela faz automaticamente a vinculação de conta e o registro do usuário no Polar Flow, após a autorização.

### Executando a aplicação web

```bash
python example_web_app.py
```

Após iniciar, navegue para [http://localhost:5000/](http://localhost:5000/)

* Na página, há botões para autorização e leitura dos dados disponíveis.
* Clique em "Link to authorize" para autorizar o acesso com as credenciais do Polar Flow.
* O Webapp suporta múltiplas contas conectadas.
  * Para conectar outra conta, saia de [https://flow.polar.com/](https://flow.polar.com/), e o botão de autorização redirecionará para uma página de login.
* Clicar no botão de autorização várias vezes enquanto estiver logado apenas relogará a conta atual, revelando um campo "Conta Vinculada".

Após a vinculação da conta, um novo arquivo [usertokens.yml] será criado para armazenar o token de acesso do usuário.

A aplicação web tem a seguinte funcionalidade:

1) Link para autorização
    * Autentica o usuário do Polar Flow. Desconecte-se para autenticar outro usuário.
2) Ler dados
   * Obtém informações do usuário
   * Obtém dados de endpoints não-transacionais, que não descartam dados após a leitura.
       * Dados incluem: exercícios, sono e recarga noturna.

## Exemplo de aplicação em console

A aplicação de console requer mais trabalho manual do que a web. A conta do usuário precisa ser vinculada ao cliente e o usuário registrado antes de qualquer dado ser acessado. O usuário é solicitado a autorizar no Polar Flow, sendo redirecionado de volta ao URL de callback da aplicação com o código de autorização.

### Vinculando e registrando o usuário

Primeiro, precisamos iniciar o serviço de callback rodando:

```bash
python authorization_callback_server.py
```

Com o serviço em execução, navegue para `https://flow.polar.com/oauth2/authorization?response_type=code&client_id=<YOUR_CLIENT_ID>` para vincular a conta e registrar o usuário. Se não estiver logado, a janela de login do Polar Flow será exibida. Caso contrário, o navegador será redirecionado para o URL de callback e a vinculação será concluída.

Após a vinculação, o arquivo [authorization_callback_server.py] pode ser fechado. O token de acesso e o ID do usuário serão automaticamente salvos no [config.yml], que ficará assim:

```bash
access_token: SEU_TOKEN_DE_ACESSO
client_id: SEU_CLIENT_ID
client_secret: SEU_CLIENT_SECRET
user_id: SEU_ID_DE_USUÁRIO_POLAR
```

### Executando a aplicação de console

```bash
python example_console_app.py
```

A aplicação em console tem as seguintes funcionalidades:

1) Obter informações do usuário
    * Informações como gênero, primeiro nome, etc.
2) Obter dados transacionais disponíveis
    * Dados de endpoints transacionais que descartam os dados após a leitura. Uma vez que você requisitou, salve os dados. Você não poderá fazer coletar esses dados exceto caso tenha nova notificação (uma nova captura ou treino)
    * Dados incluem: exercícios, resumo de atividades e informações físicas.
3) Obter dados não-transacionais disponíveis
    * Dados de endpoints não-transacionais.
    * Dados incluem: exercícios, sono e recarga noturna.
4) Revogar token de acesso
    * Revoga o token de acesso atual, exigindo nova autenticação.
5) Sair
    * Encerra a aplicação.

Uma vez que o usuário vinculou sua conta ao cliente e sincronizou os dados do dispositivo Polar com o Polar Flow, a aplicação pode carregar os dados.

## Solução de Problemas

Caso tenha dificuldades, verifique:

1) Certifique-se de **usar a versão correta do Python e PIP**.
2) Verifique se **criou e configurou corretamente o cliente de API** com seu `client_id` e `client_secret` no [config.yml].
3) Certifique-se de ter utilizado **o URL de redirecionamento correto**.

[authorization_callback_server.py]: ./authorization_callback_server.py

[config.yml]: ./config.yml

[usertokens.yml]: ./usertokens.yml

[Polar Open AccessLink]: https://www.polar.com/accesslink-api/

### Novas Features

- A possibilidade de gerar relatórios automáticos a partir dos dados sincronizados.
- Suporte aprimorado para múltiplos usuários no console e na web.
- Integração com bancos de dados externos para armazenamento seguro de tokens e dados do usuário.