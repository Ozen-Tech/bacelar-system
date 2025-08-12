#!/usr/bin/env python3
from app.db.connection import SessionLocal
from app.models.deadline.model import Deadline
from app.tasks import classify_deadline
from datetime import datetime, timedelta

def test_deadline_classification():
    db = SessionLocal()
    try:
        # Buscar todos os prazos
        deadlines = db.query(Deadline).all()
        print(f'Total de prazos no sistema: {len(deadlines)}')
        
        if deadlines:
            print('\n--- Prazos existentes ---')
            for d in deadlines[:5]:  # Mostrar apenas os primeiros 5
                days_until = (d.due_date.date() - datetime.now().date()).days
                print(f'ID: {str(d.id)[:8]}...')
                print(f'  Descrição: {d.task_description[:50]}...')
                print(f'  Data: {d.due_date.strftime("%d/%m/%Y")}')
                print(f'  Dias restantes: {days_until}')
                print(f'  Classificação atual: {d.classification}')
                print(f'  Status: {d.status}')
                print('---')
                
                # Reclassificar este prazo
                print(f'Reclassificando prazo {str(d.id)[:8]}...')
                classify_deadline.delay(str(d.id))
                
        else:
            print('Nenhum prazo encontrado no sistema.')
            
    except Exception as e:
        print(f'Erro: {e}')
    finally:
        db.close()

if __name__ == '__main__':
    test_deadline_classification()