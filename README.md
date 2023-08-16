# Servidor FHIR JPA R4 

# Parte 1- Configuração de servidor FHIR (Arquitetura)

## Configuração

Primeiramente foi realizada a configuração do arquivo localizado no seguinte caminho "..\src\main\resources\application.yaml". Este arquivo yaml é responsavel por uma seríe de configurações disponibilizadas pelos implementadores da solução.

Para este teste ajustamos a disponibilidade dos recursos de acordo com o levantamente previo realizado nos dados disponibilizados:
  - supported_resource_types: Patient e Observation

Ajustamos para que o servidor valide as requisições realizadas de acordo com o padrão FHIR R4 alterando outros 2 parâmetros especificos do application.yaml, este responsável por definir a versão do protocolo FHIR, sendo R4 o mesmo utilizado atualmente pela RNDS.
  - hapi.fhir.fhir_version: R4
  
Ajustamos também o responsável por habilitar as consistencias nas requisições de acrodo com a versão do protocolo definido.
  - hapi.fhir.validation.requests_enabled: true
.

## Deploy

O servidor HL7 FHIR implementado utiliza containers Docker devidamente configurados a partir de um arquivo Docker Composer, o qual pode ser chamado através do comando 
  - docker-compose up -d --build

Após a finalização da execução do comando, o servidor fica disponivel no seguinte endereço 
  - http://localhost:8080/.

## Banco de dados

Para esta avaliação, utilizaremos o banco de dados MySQL, o qual foi devidamente configuração no arquivo compose referente.

spring:
  datasource:
    url: 'jdbc:mysql://hapi-fhir-mysql:3306/hapi'
    username: admin
    password: admin
    driverClassName: com.mysql.jdbc.Driver
Also, make sure you are not setting the Hibernate Dialect explicitly, see more details in the section about MySQL.

# Parte 2 - Carga de dados para o Resource Patient e outros que se fizerem necessários (Integração de Dados)

Para esta etapa, foi desenvolvido um Script Python chamado ETL.py que faz todo o ETL da amostra de dados disponibilizada, fazendo uma série de etapas para processar  os dados de pacientes a partir de um arquivo CSV, 
criar recursos de interoperabilidade em saúde (FHIR) e enviá-los a um servidor FHIR local. 

Abaixo listo as principais funcionalidades do script.

## Preparação e Configuração:

O script importa os módulos necessários, incluindo csv, datetime, chardet e requests, para lidar com manipulação de dados, datas, codificação e comunicação via HTTP.

## Normalização de Dados:

A função normalize_gender é utilizada para mapear os valores de gênero "Masculino" e "Feminino" para os valores normalizados "male" e "female", ou "unknown" se o valor não for reconhecido.

## Criação de Recursos FHIR Patient:

A função create_fhir_patient é empregada para criar os recursos FHIR de paciente, contendo informações como nome, CPF, gênero, data de nascimento, telefone e país de nascimento.

## Criação de Recursos FHIR Observation:

A função create_fhir_observation é usada para criar os recursos FHIR Observation, associado a um paciente específico. Isso inclui um texto de observação e informações relacionadas.

# Processamento do Arquivo CSV:

O script lê um arquivo CSV contendo dados dos pacientes.
Detecta a codificação do arquivo usando o módulo chardet.
Decodifica o cabeçalho do CSV para lidar com caracteres acentuados.
Itera por cada linha do arquivo, extraindo informações como nome, CPF, gênero, data de nascimento, telefone, país de nascimento e observação.

# Criação e Envio de Recursos FHIR:

## Para cada linha do arquivo CSV:

Cria um recurso FHIR de paciente usando a função create_fhir_patient.
Envia os dados do paciente para um servidor FHIR local via solicitação POST.

## Se a criação do paciente for bem-sucedida:
Obtém o ID do paciente criado.
Se uma observação estiver presente na linha, cria um recurso FHIR de observação usando a função create_fhir_observation.
Envia os dados da observação para o servidor FHIR local.

## Exibição de Resultados e Feedback:

O script exibe informações de depuração, como o cabeçalho decodificado e os detalhes dos pacientes e observações criados.
Fornece feedback sobre o status da criação de pacientes e observações, incluindo mensagens de sucesso ou falha.

Em resumo, este script automatiza o processo de leitura de dados de pacientes a partir de um arquivo CSV, criação de recursos FHIR de pacientes e observações, e envio esses recursos para um servidor FHIR local, com a capacidade de lidar com diferentes codificações de caracteres e gerar feedback sobre o processo de criação.