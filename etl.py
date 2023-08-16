import csv
from datetime import datetime
import chardet
import requests

def normalize_gender(gender):
    gender_map = {
        "Masculino": "male",   # Mapeia "Masculino" para "male"
        "Feminino": "female"   # Mapeia "Feminino" para "female"
    }
    return gender_map.get(gender, "unknown")  # Retorna o valor correspondente no mapa, ou "unknown" se não encontrado

def create_fhir_patient(name, cpf, gender, birthdate, phone, country):
    patient = {
        "resourceType": "Patient",   # Tipo de recurso: Paciente
        "identifier": [
            {
                "system": "http://www.saude.gov.br/fhir/r4/NamingSystem/cpf",
                "value": cpf    # Identificador do paciente: CPF
            }
        ],
        "name": [
            {
                "use": "official",  # Uso oficial do nome
                "text": name,       # Nome do paciente
            }
        ],
        "gender": normalize_gender(gender),   # Gênero do paciente (normalizado para "male", "female" ou "unknown")
        "birthDate": birthdate,   # Data de nascimento do paciente (no formato YYYY-MM-DD)
        "telecom": [
            {
                "system": "phone",   # Sistema de comunicação: telefone
                "value": phone       # Número de telefone do paciente
            }
        ],
        "address": [
            {
                "country": country   # País de nascimento do paciente
            }
        ]
    }
    return patient

def create_fhir_observation(patient_id, observation_text):
    observation = {
        "resourceType": "Observation",   # Tipo de recurso: Observação
        "status": "final",   # Status da observação: finalizado
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "60591-5",
                    "display": "Patient summary"   # Código e descrição da observação
                }
            ],
            "text": "Patient summary"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"   # Referência ao paciente relacionado a esta observação
        },
        "valueString": observation_text   # Valor da observação (texto)
    }
    return observation

def main():
    csv_file = "patients.csv"   # Arquivo CSV contendo os dados dos pacientes

    with open(csv_file, "rb") as file:
        result = chardet.detect(file.read())
    
    encoding = result['encoding']   # Determina a codificação do arquivo
    
    with open(csv_file, newline='', encoding=encoding) as file:
        csv_reader = csv.DictReader(file)   # Cria um leitor de CSV com dicionário
        
        # Decodifica o cabeçalho manualmente para lidar com acentuação
        header = [col.encode(encoding).decode(encoding) for col in csv_reader.fieldnames]
        print(header)  # Imprime o cabeçalho decodificado para depuração
        
        for row in csv_reader:
            name = row['Nome']   # Obtém o nome do paciente
            cpf = row['CPF']   # Obtém o CPF do paciente
            gender = row[header[2]]   # Obtém o gênero do paciente usando o índice decodificado para 'Gênero'
            birthdate = datetime.strptime(row['Data de Nascimento'], '%d/%m/%Y').strftime('%Y-%m-%d')  # Converte a data de nascimento para o formato apropriado
            phone = row['Telefone']   # Obtém o número de telefone do paciente
            country = row[header[5]]   # Obtém o país de nascimento do paciente usando o índice decodificado para 'País de Nascimento'
            observation = row[header[6]]   # Obtém a observação do paciente usando o índice decodificado para 'Observação'
            
            patient = create_fhir_patient(name, cpf, gender, birthdate, phone, country)   # Cria o recurso FHIR do paciente
            print(patient)   # Imprime o paciente para depuração
            
            # Envia os dados do paciente para o servidor FHIR
            fhir_endpoint_patient = 'http://localhost:8080/fhir/Patient'
            response_patient = requests.post(fhir_endpoint_patient, json=patient)   # Envia uma solicitação POST com os dados do paciente
            
            if response_patient.status_code == 201:   # Verifica se o paciente foi criado com sucesso
                patient_id = response_patient.json().get('id')   # Obtém o ID do paciente do JSON de resposta
                print("Patient created successfully. Patient ID:", patient_id)
                
                if observation.strip():   # Verifica se a observação não está vazia ou contém apenas espaços em branco
                    # Cria e envia a Observação relacionada ao Paciente
                    observation_data = create_fhir_observation(patient_id, observation)
                    fhir_endpoint_observation = 'http://localhost:8080/fhir/Observation'
                    response_observation = requests.post(fhir_endpoint_observation, json=observation_data)   # Envia uma solicitação POST com os dados da observação
                    
                    if response_observation.status_code == 201:   # Verifica se a observação foi criada com sucesso
                        print("Observation created successfully.")
                    else:
                        print("Failed to create Observation. Response status:", response_observation.status_code)
                        print("Response text:", response_observation.text)
                else:
                    print("No Observation provided. Skipping Observation creation.")
            else:
                print("Failed to create Patient. Response status:", response_patient.status_code)
                print("Response text:", response_patient.text)
            
            print("=" * 40)

if __name__ == "__main__":
    main()
