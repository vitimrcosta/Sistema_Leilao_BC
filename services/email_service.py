class EmailService:
    #Método estático
    #É independente do estado da classe ou do objeto (não usa atributos da classe ou instância).
    # Pode ser chamado diretamente pela classe, sem precisar criar um objeto.
    @staticmethod
    def enviar(destinatario: str, assunto: str, mensagem: str):
        print(f"📧 E-mail enviado para {destinatario}:")
        print(f"Assunto: {assunto}")
        print(f"Mensagem: {mensagem}\n")
