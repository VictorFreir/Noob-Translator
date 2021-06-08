import speech_recognition as sr
import os
from ibm_watson import SpeechToTextV1, LanguageTranslatorV3, TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pyglet


#Para deixar mais legível o código estará organizado em um classe com funções
class Translator:
    def __init__(self):
        self.languages = {'0':['ar','Árabe','ar-AR_BroadbandModel','ar-AR_OmarVoice'], '1':['zh','Chinês','zh-CN_BroadbandModel','zh-CN_WangWeiVoice'], '2':['es','Espanhol','es-AR_BroadbandModel','es-LA_SofiaV3Voice'], '3':['fr','Francês','fr-FR_BroadbandModel','fr-FR_ReneeVoice'], '4':['it','Italiano','it-IT_BroadbandModel','it-IT_FrancescaVoice'], '5':['ja','Japonês','ja-JP_BroadbandModel','ja-JP_EmiVoice'], '6':['pt','Português','pt-BR_BroadbandModel','pt-BR_IsabelaVoice'], '7':['en','Inglês','en-US_BroadbandModel','en-US_AllisonVoice'],'8':['nl','Holandês','nl-NL_BroadbandModel','nl-NL_EmmaVoice']}
        
        #Conexão com API de voz para texto
        self.url_s2t = '' #URL da API speech to text da IBM
        self.apikey_s2t = '' # Key da API speech to text da IBM
        self.filename = 'audio.wav'

        #Conexão com a API de traduçãp
        self.apikey_translator = ''
        self.url_translator = ''
        self.version_translator = '2020-10-24'

        #Conexão com API de texto para voz
        self.apikey_t2s = ''
        self.url_t2s = ''

        self.again = True        
        return

    #Menu de seleção de linguagem
    def language_menu(self):#
        print('\033[1;97m Olá, para começarmos com o seu serviço de tradução, precisamos configurar algumas coisinhas... \n')
        print('\033[1;95m Primeiramente, você precisa selecionar o primeiro idioma, digite:')
        self.first_language = self.get_language() #A key da primeira lingua do diiocionario languages
        self.first_model_id = self.languages[str(self.first_language-1)][0] #O model_id da primeira lingua
        self.first_model = self.languages[str(self.first_language-1)][2] # O model da primeira lingua
        

        #Começa o segundo menu de seleção de idioma
        print('Ótimo, primeiro idioma selecionado! \n')
        print('\033[1;95mAgora, selecione o segundo idioma, digite:')
        self.second_language = self.get_language()
        self.second_model_id = self.languages[str(self.second_language-1)][0]
        self.second_voice = self.languages[str(self.second_language-1)][3]
        print('Perfeito, segundo idioma selencionado!\n')
        return


    #Mensagem de opção inválida
    def error_message(self): #Mensagem de erro seguida da saída do programa
        os.system('cls' if os.name == 'nt' else 'clear')
        print('\033[1;31mA opcão digitada foi inválida! \nReinicie o programa e digite uma opção válida. \033[1;97m')
        quit()
        return


    #Pega o idioma selecionado
    def get_language(self): #Busca o idioma
        
        #Chama as opções de idiomas
        with open('primeiromenu.txt', 'r',encoding = 'utf-8') as menu:
            print('\033[1;97m'+menu.read())

        #Pega a opção 
        self.language = input()
        
        #Checa se é um opção válida:
        try:
            self.language = int(self.language)
            if self.language>9 or self.language<1:
                self.error_message()

        #Caso não seja um número 
        except:
            self.error_message()
        os.system('cls' if os.name == 'nt' else 'clear')
        return self.language

    
    #Agora vamos começar a gravar o áudio
    def listen_mic(self): #Ouvir e gravar a fala
        print('Estou ouvindo... \nPode falar!')
        self.mic = sr.Recognizer()

        with sr.Microphone() as source:

            self.mic.adjust_for_ambient_noise(source)    
            self.audio = self.mic.listen(source)

        with open('audio.wav','wb') as f:
            f.write(self.audio.get_wav_data())
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Ouvi tudo! \n\033[1;95mJá estou traduzindo \nEspera um minutinho...\033[1;97m')        
        return


    #Agora, vamos começar o reconhecimento, transformando audio em texto
    def to_text(self, model):
        #Autenticação e estabelecimento de conexão com a API
        self.authenticator = IAMAuthenticator(self.apikey_s2t)
        self.s2t = SpeechToTextV1(self.authenticator)
        self.s2t.set_service_url(self.url_s2t)
        
        with open(self.filename, mode='rb') as wav:
            self.model = model
            self.response = self.s2t.recognize(audio = wav, content_type = 'audio/wav', model=self.model)
            self.text = self.response.result['results'][0]['alternatives'][0]['transcript']
        return self.text


    #Agora, vamos traduzir o texto para a segunda linha
    def translator(self, from_language,to_language):# Refazer isso para traduzir para ingles e depois de ingles para a segunda linha
        #Autenticação e conxeção com a API
        self.authenticator_lt = IAMAuthenticator(self.apikey_translator)
        self.language_tranlator = LanguageTranslatorV3(version = self.version_translator, authenticator = self.authenticator_lt)
        self.language_tranlator.set_service_url(self.url_translator)
        
        try:
            #Define model id
            self.model_id = from_language+'-'+to_language
            
            #Traduz
            self.translation = self.language_tranlator.translate(text = self.text, model_id = self.model_id)
            
            #Seleciona apenas o texto traduzido
            self.translation_result = self.translation.result['translations'][0]['translation']
        except:
            return
        return
    

    #Transforma a tradução em audio
    def to_audio(self,voice): 
        #Estabelecendo a conexão com a API de texto para audio
        self.authenticator = IAMAuthenticator(self.apikey_t2s)
        self.text_to_speech = TextToSpeechV1(authenticator=self.authenticator)
        self.text_to_speech.set_service_url(self.url_t2s)

        with open('filename.wav','wb') as audio_file:
            audio_file.write(self.text_to_speech.synthesize(self.translation_result,voice=voice,accept='audio/mp3').get_result().content)
        return


    #Roda o audio traduzido para o não falante ouvir
    def run_audio(self): 
        os.system('cls' if os.name == 'nt' else 'clear')
        print('\033[1;95mTradução:','\033[1;97m'+self.translation_result)       
        self.audio_translate = pyglet.resource.media('filename.wav')
        self.audio_translate.play()
        #pyglet.app.run()
        return


    # Verifica se vai traduzir novamente ou não
    def translate_again(self):
        print('\033[1;97mDeseja traduzir algo mais?')
        self.again_verify = input('\nDigite "S" para sim e "N" para não: ') # Verifica se vai repetir 
        if self.again_verify.lower() == 's':
            self.again = True
        elif self.again_verify.lower() == 'n':
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Estarei aqui na próxima!')
            quit()
        else:
            self.error_message()
        return


    # Reseta as configurações
    def reset_config(self):
        os.remove('audio.wav')
        os.remove('filename.wav')
        return

    #Roda o programa completo
    def run_program(self):
        self.language_menu()
        while self.again:
            self.listen_mic()
            self.to_text(self.first_model)
            self.translator(self.first_model_id,'en')
            self.translator('en',self.second_model_id)
            self.to_audio(self.second_voice)
            self.run_audio()
            self.translate_again()
            self.reset_config()
        return


main = Translator()
main.run_program()