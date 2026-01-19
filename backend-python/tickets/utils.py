from datetime import datetime, timedelta
import holidays

def calcular_prazo_uteis(data_inicio, horas_sla):
    """
    Calcula data limite ignorando:
    1. Finais de Semana
    2. Horário não-comercial (antes das 08h e depois das 18h)
    3. FERIADOS NACIONAIS (Brasil)
    """
    INICIO_EXPEDIENTE = 8
    FIM_EXPEDIENTE = 18
    
    # feriados do Brasil
    feriados_br = holidays.BR() 
    
    cursor = data_inicio
    horas_restantes = horas_sla

    def eh_dia_improdutivo(data):
        if data.weekday() >= 5:
            return True
        if data in feriados_br:
            return True
        return False

    while True:
        # sabado, domingo ou feriado
        if eh_dia_improdutivo(cursor):
            cursor += timedelta(days=1)
            cursor = cursor.replace(hour=INICIO_EXPEDIENTE, minute=0, second=0)
            continue
        
        # antes das 08:00
        if cursor.hour < INICIO_EXPEDIENTE:
            cursor = cursor.replace(hour=INICIO_EXPEDIENTE, minute=0, second=0)
            break 
            
        # depois das 18:00
        if cursor.hour >= FIM_EXPEDIENTE:
            cursor += timedelta(days=1)
            cursor = cursor.replace(hour=INICIO_EXPEDIENTE, minute=0, second=0)
            continue 
            
        break

    # consome as horas do SLA
    while horas_restantes > 0:
        fim_do_dia_atual = cursor.replace(hour=FIM_EXPEDIENTE, minute=0, second=0)
        
        segundos_disponiveis_hoje = (fim_do_dia_atual - cursor).total_seconds()
        horas_disponiveis_hoje = segundos_disponiveis_hoje / 3600
        
        if horas_restantes <= horas_disponiveis_hoje:
            cursor += timedelta(hours=horas_restantes)
            horas_restantes = 0
        else:
            horas_restantes -= horas_disponiveis_hoje
            
            cursor += timedelta(days=1)
            cursor = cursor.replace(hour=INICIO_EXPEDIENTE, minute=0, second=0)
            
            # se for feriado ou fim de semana, pula até achar dia útil
            while eh_dia_improdutivo(cursor):
                cursor += timedelta(days=1)

    return cursor