
<div align="center">

# 🛡️ PySupport | Secure Help Desk System

### Um Service Desk corporativo com arquitetura híbrida, foco em SLA realista e segurança

<br>

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" title="Python 3.14" width="60" height="60"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/django/django-plain.svg" alt="Django" title="Django 5.0" width="60" height="60"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg" alt="Java" title="Java 17" width="60" height="60"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/spring/spring-original.svg" alt="Spring Boot" title="Spring Boot 3" width="60" height="60"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" alt="PostgreSQL" title="PostgreSQL 16" width="60" height="60"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" alt="Docker" title="Docker Container" width="60" height="60"/>
</p>

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" alt="HTML5" title="HTML5" width="50" height="50"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" alt="CSS3" title="CSS3" width="50" height="50"/>
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" alt="JavaScript" title="JavaScript ES6+" width="50" height="50"/>
</p>

[Sobre o Projeto](#sobre) • [Funcionalidades](#funcionalidades) • [SLA](#sla) • [Galeria](#galeria) • [Instalação](#instalacao)

</div>

<br>

---

<div id="sobre"></div>

## 💡 Visão Geral

O **PySupport** é um sistema de **Help Desk / Service Desk corporativo**, desenvolvido com foco em **boas práticas reais de mercado**: separação de responsabilidades, segurança, regras de negócio claras e métricas confiáveis.

O objetivo do projeto não é apenas “abrir chamados”, mas **simular um ambiente profissional**, onde:

* SLAs seguem horários comerciais reais
* A autenticação é tratada como um ponto crítico de segurança
* Usuários possuem permissões bem definidas
* Métricas ajudam na tomada de decisão

Trata-se de um projeto **full stack**, funcional e pronto para produção, ideal para demonstrar domínio técnico em processos de TI.

---

<div id="funcionalidades"></div>

## ✨ Funcionalidades Principais

* 🔐 **Login seguro em duas camadas** O acesso ao sistema é validado por um serviço separado, aumentando a segurança dos dados.

* ⏱️ **Controle inteligente de prazos (SLA)** O sistema calcula automaticamente o tempo de atendimento considerando horário comercial, finais de semana e feriados.

* 👥 **Gestão completa de usuários e setores**
  - Criar, editar, remover usuários e setores
  - Definir grupos e níveis de acesso
  - Exportar relatórios de usuários e chamados em **Excel (.xlsx)**

* 📊 **Dashboard com indicadores em tempo real** Visão geral dos chamados com números claros e gráficos para facilitar decisões rápidas.

* 🖼️ **Envio de arquivos facilitado** É possível anexar arquivos, arrastar documentos ou até colar prints diretamente no chamado (**Ctrl+V**).

* 🏢 **Acesso por setor e função** Cada usuário vê apenas os chamados relacionados ao seu setor, garantindo organização e privacidade.

* 🧾 **Histórico completo dos chamados** Todas as interações ficam registradas com data e hora, garantindo rastreabilidade.

* 🌙 **Modo claro e escuro** O sistema salva automaticamente a preferência de tema do usuário.

---

<div id="sla"></div>

## ⚙️ SLA e Horas Úteis

O cálculo de SLA é um dos pontos centrais do projeto. O tempo **não é contado de forma linear**, evitando distorções comuns em sistemas simples.

### ⏳ Prioridades

| Prioridade | SLA      | Descrição                        |
| ---------- | -------- | -------------------------------- |
| 🔴 Alta    | 6 horas  | Incidente crítico / parada total |
| 🟡 Média   | 16 horas | Impacto parcial na operação      |
| 🟢 Baixa   | 30 horas | Dúvidas, acessos e solicitações  |

### 📅 Regras de Contagem

* Horário comercial: **08:00 às 18:00**
* Sábados e domingos são ignorados
* Feriados pausam a contagem

> **Exemplo:** um chamado com **Prioridade Alta** aberto às 17h de sexta-feira vence apenas às **13h da segunda-feira seguinte.**

---

<div id="galeria"></div>

## 📸 Galeria

<div align="center">

| Login                                                | Dashboard                               |
| ---------------------------------------------------- | --------------------------------------- |
| <img src="./img/login.png" width="100%"> | <img src="./img/home_page.png" width="100%"> |

<br>

| Chamado                                           | Gestão de Usuários                          |
| ------------------------------------------------- | ------------------------------------------- |
| <img src="./img/editar_chamado.png" width="100%"> | <img src="./img/usuarios.png" width="100%"> |

</div>

---

## 🏗️ Arquitetura Híbrida

O fluxo de login é interceptado pelo Front-end, que consulta o microsserviço Java antes de permitir a criação da sessão no Django.

```mermaid
sequenceDiagram
    participant User as 👤 Usuário (Browser)
    participant Java as ☕ API Java (Auth)
    participant DB as 🗄️ PostgreSQL
    participant Py as 🐍 Django (Core)

    User->>User: Preenche Login/Senha
    User->>Java: POST /auth/login (JSON)
    Java->>DB: Verifica Hash da Senha (BCrypt)
    DB-->>Java: Retorna Validação
    alt Senha Correta
        Java-->>User: 200 OK + Token
        User->>Py: Submete Form (Session Create)
        Py-->>User: Redireciona p/ Dashboard
    else Senha Incorreta
        Java-->>User: 401 Unauthorized
        User->>User: Exibe Erro (Sem tocar no Django)
    end

```

---

## 🛠️ Tecnologias Utilizadas

### Backend

* **Python 3.14 + Django 5.0** Responsáveis pela lógica principal do sistema, regras de negócio, telas, controle de usuários e fluxo dos chamados.
* **Bibliotecas de data e tempo** Utilizadas para calcular prazos de atendimento (SLA), considerando horário comercial, finais de semana e feriados.
* **Pandas / OpenPyXL** Usadas para gerar relatórios e exportações de dados em formato **Excel (.xlsx)**.
* **Java 17 + Spring Boot 3** Microsserviço responsável pela autenticação e validação segura de credenciais via API REST.
* **PostgreSQL** Banco de dados relacional onde todas as informações do sistema são armazenadas de forma segura e estruturada.

---

### Frontend

* **HTML5 / CSS3 (Bootstrap 5.3)** Estrutura e estilo das telas, com layout limpo e visual moderno.
* **JavaScript (ES6+)** Comunicação assíncrona com o backend, atualização dinâmica da interface e melhor experiência do usuário.
* **Jinja2** Motor de templates utilizado pelo Django para renderizar páginas dinâmicas.

---

### DevOps & Tools

* **Docker** Containerização da aplicação, facilitando execução local e deploy em qualquer ambiente.
* **Render (PaaS)** Plataforma de nuvem utilizada para publicar a aplicação em produção.
* **Neon Tech** Banco de dados PostgreSQL serverless, garantindo escalabilidade e disponibilidade.
* **Git / GitHub** Controle de versão, histórico do projeto e colaboração.

---

<div id="instalacao"></div>

## 🚀 Instalação e Execução

Você pode rodar este projeto localmente usando Docker (recomendado) ou manualmente.

### Pré-requisitos

* Python 3.10+
* Java JDK 17+
* PostgreSQL

<details>
<summary><strong>🐳 Opção 1: Rodar Banco de Dados (Docker)</strong></summary>

Se você não quiser instalar o Postgres na máquina, rode:

```bash
docker run --name pysupport-db -e POSTGRES_PASSWORD=admin -e POSTGRES_DB=pysupport_db -p 5432:5432 -d postgres

```

</details>

<details>
<summary><strong>☕ Opção 2: Rodar Backend Java (Auth API)</strong></summary>

1. Entre na pasta:

```bash
cd backend-java

```

2. Configure o banco em `src/main/resources/application.properties` (ou use variáveis de ambiente).
3. Rode a aplicação:

```bash
./mvnw spring-boot:run

```

*A API ficará disponível em `http://localhost:8080*`

</details>

<details>
<summary><strong>🐍 Opção 3: Rodar Backend Python (Django Core)</strong></summary>

1. Entre na pasta:

```bash
cd backend-python

```

2. Crie o ambiente virtual e instale as dependências:

```bash
python -m venv venv
# Windows:
source venv/Scripts/activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

```

3. Rode as migrações e o servidor:

```bash
python manage.py migrate
python manage.py runserver

```

*O sistema ficará disponível em `http://127.0.0.1:8000*`

</details>

---

<div align="center">

### Developed by Gustavo Percoski

<a href="https://www.linkedin.com/in/gustavo-percoski/" target="_blank">
<img src="https://img.shields.io/badge/LinkedIn-000000?style=for-the-badge&logo=linkedin&logoColor=white" />
</a>
&nbsp;
<a href="mailto:gustavopercoski2@gmail.com">
<img src="https://img.shields.io/badge/Gmail-000000?style=for-the-badge&logo=gmail&logoColor=white" />
</a>
&nbsp;
<a href="https://github.com/gustavopercoski2-prog" target="_blank">
<img src="https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=white" />
</a>

</div>

---
