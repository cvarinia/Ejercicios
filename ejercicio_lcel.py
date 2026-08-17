import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


#Llamo al modelo
# Se usa ChatGoogleGenerativeAI en lugar de ChatOpenAI/ChatAnthropic porque no cuento con créditos pagos en esas plataformas.
# Cumple el mismo rol dentro de LCEL: es intercambiable sin tocar el resto del pipeline (prompt | modelo | parser).
modelo = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.7
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sos un asistente útil y conciso. Respondé siempre en español."),
    ("human", "{pregunta}")
])

#Primero creás una instancia del parser
parser = StrOutputParser()

#Despues el pipe
chain = prompt | modelo | parser

async def main():
    respuesta = await chain.ainvoke({"pregunta": "¿Qué es LCEL en LangChain?"})
    print(respuesta)

if __name__ == "__main__":
    asyncio.run(main())