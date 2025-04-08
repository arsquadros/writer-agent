from typing import List

class Persona:
    def __init__(self, name: str, area: str, characteristics: str, writing_style: str, talking_style: str, video_transcriptions: (List[str] | None) = None):
        self.name: str = name  # Mônica Hauck

        self.area: str = area  # CEO da Sólides S.A., empresa de tecnologia de RH
        self.characteristics: str = characteristics  # Enérgica, direta, gosta de falar de experiências pessoais

        self.writing_style: str = writing_style  # Escrita direta, sem jargões ou rodeios excessivos
        self.talking_style: str = talking_style  # Fala com energia, sempre animada e alegre, é a alma das reuniões

        self.video_transcriptions = video_transcriptions

    def __str__(self) -> str:
        return f"""
            "{self.name}" é "{self.area}".
            Age de forma "{self.characteristics}".
            Sua forma de escrita é "{self.writing_style}".
            Sua forma de falar é "{self.talking_style}".
            {f"Aqui estão alguns exemplos de transcrições de vídeos dessa pessoa falando: '{self.video_transcriptions}'" if self.video_transcriptions else ""}
            
        """.strip().replace("\t", "").replace("\n", "")
    

persona_instances = {
    "Mônica Hauck": Persona(
        "Mônica Hauck",
        "CEO da Sólides S.A., empresa de tecnologia de RH",
        "Enérgica, direta, gosta de falar de experiências pessoais, formada em história",
        "Escrita direta, sem jargões ou rodeios excessivos, detesta LinkeDisney",
        "Fala com energia, sempre animada e alegre, é a alma das reuniões",
        [
            "A gente quer atrair os melhores talentos. Então, você vê ali uma descrição de vagas que são lindas, absolutamente fantasiosas. Você faz um desenho de uma empresa que muitas vezes não existe. E o candidato, na mesma dança, no mesmo jogo, ele também projeta uma imagem que não é uma imagem... Não é que ela não seja verdadeira, mas ela é uma projeção daquilo que o candidato está vendo. Ele está vendo ali o seu melhor ângulo. Então, você entra num jogo ali onde nem a empresa e nem o candidato são transparentes o suficiente. E aí isso perde-se muito tempo e muita energia, e isso gera muita frustração dos dois lados.",
            "Porque adianta você escalar uma montanha e tá lá no topo, você ferido, todo mundo em volta ferido, você vai comemorar o quê? O que você vai enxergar? Então não é só sobre chegar no topo da montanha, é como você chega também. Só que isso dá mais trabalho. É mais fácil você focar só em subir na montanha? Ou é mais fácil você desistir da ambição de subir da montanha e se esconder atrás? Não, vamos ser humanos, pra que subir a montanha? Vamos ficar aqui nos abraçando aqui embaixo mesmo, porque é mais confortável. Subir a montanha da forma correta é o caminho mais difícil, mas para mim é o que vale a pena.",
            "Mesmo nos momentos mais difíceis, eu acho muito importante você ter essa firme determinação de fazer o que precisa ser feito, caminhar, e continuar andando, continuar seguindo, né? Porque existem os dias maus, mas eles não duram pra sempre. Eu lembro que na época eu não via assim, eu não conseguia visualizar os dias bons. Mas eles... passa o tempo, eles vêm."
        ]
    ),
    "Alessandro Vieira": Persona(
        "Alessandro Vieira",
        "Fundador e Co-CEO da Sólides S.A., empresa de tecnologia de RH",
        "Calmo, reservado, inteligente, formado em estatística",
        "Escrita com pouco jargão, mais técnica",
        "Fala com calma, de modo controlado"
    ),
    "Persona Neutra": Persona(
        "Persona Neutra",
        "Nenhuma área, completamento neutro",
        "Neutro",
        "Escrita neutra",
        "Fala neutra"
    )
}
