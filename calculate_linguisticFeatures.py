import numpy as np
import pandas as pd
import spacy
import re
# from spacy_syllables import SpacySyllables

from spellchecker import SpellChecker # pip install pyspellchecker

import os
    
    
class linguisticFeatures:
    
    def __init__(self, language = "en"):
        
        self.language = language
        
        if self.language == "pt":
            model_name = "pt_core_news_lg"
        if self.language == "en":
            model_name = "en_core_web_lg"
            
        self.nlpModel = self.check_and_load_spacy_model(model_name)
                        
    def check_and_load_spacy_model(self, model_name):
        """Verifica se o modelo pt_core_news_sm está instalado, caso contrário, instala automaticamente.
        """
        
        # Verifica se o modelo está disponível
        if model_name not in spacy.util.get_installed_models():
            print(f"Modelo {model_name} não encontrado. Instalando...")
            spacy.cli.download(model_name)
        
        # Carrega o modelo
        nlp = spacy.load(model_name)
        # nlp.add_pipe("syllables")
        
        return nlp
    
    def __name_functions(self, titles):
        """Returns functions and property names"""
        names = ['count_tokens',
                'count_types',
                'avg_word_length',
                'count_sentences',
                'avg_sentence_length',
                'count_tokens_by_pos',
                'count_stopwords',
                'count_misspellings',
                'avg_pausality',
                # 'positivity',
                # 'negativity',
                'uncertainty',
                'nonImmediacy_individualReferences',
                'nonImmediacy_groupReferences',
                'preprocess'
                ]
        functions = [self.count_tokens,
                self.count_types,
                self.avg_word_length,
                self.count_sentences,
                self.avg_sentence_length_words,
                self.count_tokens_by_pos_all,
                self.count_stopwords,
                self.count_misspellings,
                self.calculate_pausability,
                # self.calculate_positivity,
                # self.calculate_negativity,
                self.calculate_uncertainty,
                self.calculate_nonImmediacy_individualReferences,
                self.calculate_nonImmediacy_groupReferences,
                self.pre_process_text]
        requested = []
        if len(titles) == 0:
            requested = functions
            titles = names
        else:
            for a in titles:
                requested.append(functions[names.index(a)])
        return requested, titles
    
    def get(self, dataset, *args):
        """
            Retorna resultado de funções morfológicas para um dataset textual
            Funções:
                count_tokens
                
                count_types
                
                avg_word_length
                
                count_sentences
                
                avg_sentence_length
                
                count_tokens_by_pos (VERB, NOUN, ADJ, ADV, PRON)
                
                count_stopwords
                
                count_misspellings
                
                avg_pausality
                
                # positivity
                
                # negativity
                
                uncertainty
                
                nonImmediacy_individualReferences
                
                nonImmediacy_groupReferences
                
                preprocess
        """
        requested, names = self.__name_functions(args)
        
        if isinstance(dataset, str):
            dataset = [dataset]
    
        docs = self.nlpModel.pipe(dataset)
        
        values = {}
        for name in names:
            if name == 'count_tokens_by_pos':
                values['count_verbs'] = np.zeros(len(dataset))
                values['count_nouns'] = np.zeros(len(dataset))
                values['count_adjectives'] = np.zeros(len(dataset))
                values['count_adverbs'] = np.zeros(len(dataset))
                values['count_pronouns'] = np.zeros(len(dataset))
                continue
            if name == 'preprocess': 
                values[name] = ['' for i in range(len(dataset))]
                continue
            values[name] = np.zeros(len(dataset))
        
        for i, doc in enumerate(docs):
            for n, func in enumerate(requested):
                if names[n] == 'count_tokens_by_pos':
                    temp = func(doc)
                    values['count_verbs'][i] = temp['count_verbs']
                    values['count_nouns'][i] = temp['count_nouns']
                    values['count_adjectives'][i] = temp['count_adjectives']
                    values['count_adverbs'][i] = temp['count_adverbs']
                    values['count_pronouns'][i] = temp['count_pronouns']
                    continue
                values[names[n]][i] = func(doc)
                
        return values
    
    def saveAll(self, dataset, datasetName, path):
        
        features = self.get(dataset)

        # Criar um DataFrame a partir das features
        features['dataset'] = datasetName
        df = pd.DataFrame([features])  # Transformar em DataFrame, com uma linha de dados
        
        # Mover a coluna 'dataset' para a primeira posição
        columns = ['dataset'] + [col for col in df.columns if col != 'dataset']
        df = df[columns]
    
        # Verifica se o arquivo já existe
        if not os.path.exists(path):
            # Se não existe, cria o arquivo e escreve o cabeçalho
            df.to_csv(path, index=False, float_format='%.3f', mode='w', header=True)
        else:
            # Se já existe, apenas adiciona a nova linha
            df.to_csv(path, index=False, float_format='%.3f', mode='a', header=False)        
    
    def avg_features(self, func, dataset, *args):
        
        values = [ func(text, *args) for text in dataset]
                
        return np.sum(values) / len(dataset) 
    
    def calcAll_dataset(self, func, dataset, *args):
        """Calcula uma determinada feature em toda base de dados"""
    
        values = []
        values.extend( [ func(text, *args) for text in dataset ] )
        
        values = self.flatten(values)
        
        return values
    
    def flatten(self, lista_de_listas):
        """Converte uma lista de listas (ou valores individuais) em uma única lista."""
        result = []
        for item in lista_de_listas:
            if isinstance(item, list):
                result.extend(item)  # Se for uma lista, adiciona seus itens
            else:
                result.append(item)  # Se não for uma lista, adiciona o valor diretamente
        return result
            
    def count_tokens(self, doc):
        """Conta o número de tokens em português usando spaCy"""
    
        # Conta os tokens para cada documento na lista
        token_counts = len(doc)
        
        return token_counts
    
    def count_types(self, doc):
        """Conta o número de tipos (palavras únicas) excluindo pontuação e números usando spaCy"""    
        
        # Conta os tipos para cada texto na lista
        type_counts = len({token.text.lower() for token in doc if token.is_alpha})
    
        return type_counts
    
    def avg_word_length(self, doc):
        """Calcula o tamanho médio das palavras em caracteres, excluindo pontuação e números"""

        # Extrai as palavras (ignorando pontuação e números)
        words = [token.text for token in doc if token.is_alpha]
        
        # Calcula o comprimento de cada palavra
        word_lengths = np.mean([len(word) for word in words])
        
        return word_lengths
    
    def count_sentences(self, doc):
        """Counts the count of sentences in a text."""
           
        # Conta o número de sentenças para cada texto na lista
        sentence_counts = len(list(doc.sents))
    
        return sentence_counts


    def avg_sentence_length_words(self, doc):
        """Return the size of the sentences"""

        # Calcula o tamanho de cada sentença (número de palavras)
        sentences_length = np.mean([len([token for token in sent if token.is_alpha]) for sent in doc.sents])
        
        return np.array(sentences_length)
    
    def count_tokens_by_pos_all(self, doc):
        count = {}
        count['count_verbs'] = self.count_tokens_by_pos(doc, "VERB")
        count['count_nouns'] = self.count_tokens_by_pos(doc, "NOUN")
        count['count_adjectives'] = self.count_tokens_by_pos(doc, "ADJ")
        count['count_adverbs'] = self.count_tokens_by_pos(doc, "ADV")
        count['count_pronouns'] = self.count_tokens_by_pos(doc, "PRON")
        return count
    
    def count_tokens_by_pos(self, doc, pos_tag):
        """Calcula o número de tokens de uma determinada classe gramatical em um texto usando spaCy"""
        
        # Conta o número de tokens para cada texto na lista
        token_counts = sum(1 for token in doc if token.pos_ == pos_tag)
    
        return token_counts

    
    def count_stopwords(self, doc):
        """Calcula o número de stopwords em um texto usando spaCy"""
        
        # Conta o número de stopwords para cada texto na lista
        stopword_counts = sum(1 for token in doc if token.is_stop)
    
        return stopword_counts
    
    def count_misspellings(self, doc):
        """Identifica palavras com erros ortográficos em um texto"""
        
        spell = SpellChecker(language=self.language)  # Definir o idioma como portuguêsn
        
        # Conta o número de erros ortográficos para cada texto na lista
        misspellings_counts = len(spell.unknown([token.text for token in doc if token.is_alpha]))
        
        return misspellings_counts
    
    def calculate_pausability(self, doc):
        """Calculates the pausability of a text: count of punctuation marks over the count of sentences."""
        num_punctuation = sum(1 for token in doc if token.is_punct)  # Contar marcas de pontuação
        num_sentences = len(list(doc.sents))  # Contar sentenças
        
        return num_sentences
    
    # def calculate_positivity(self, doc):
        
    #     liwc = LIWC()
    #     lexicon = liwc.get_PosNeg()
    #     positivity = 0
        
    #     for token in doc:
    #         if str(token) in lexicon['posemo']:
    #             positivity += 1

    #     return positivity
    
    # def calculate_negativity(self, doc):
        
    #     liwc = LIWC()
    #     lexicon = liwc.get_PosNeg()
    #     negativity = 0
        
    #     for token in doc:
    #         if str(token) in lexicon['negemo']:
    #             negativity += 1

    #     return negativity
            

    def count_modal_verbs(self, doc):
        """Counts the count of modal verbs in a Portuguese text using spaCy."""

        # List of common Portuguese modal verbs (lemmas)
        modal_verbs = {"poder", "dever", "precisar", "ter", "haver"}

        # Conta ocorrências de verbos modais com base no lema
        modal_count = sum(1 for token in doc if token.pos_ == "VERB" and token.lemma_ in modal_verbs)
        
        return modal_count
    
    def calculate_uncertainty(self, doc):
        
        # Conta o número de verbos modais e verbos
        nModalVerbs = self.count_modal_verbs(doc)
        
        # Contar voz passiva: verbos auxiliares seguidos de um particípio
        n_passive_voice = sum(1 for i, token in enumerate(doc[:-1]) if token.pos_ == "VERB" and token.lemma_ in ["ser", "estar"] and doc[i+1].tag_ == "VBN")
        
        # Calcula a incerteza (razão entre verbos modais e verbos)
        uncertainty = nModalVerbs + n_passive_voice 
        
        return uncertainty
    
    def calculate_nonImmediacy_individualReferences(self, doc):
        # Conta o número de pronomes de 1ª pessoa (token.person == 1)
        first_person_count = sum(1 for token in doc if token.pos_ == "PRON" and "1" in token.morph.get("Person") and token.morph.get("count") == ["Sing"])
        
        # Conta o número de pronomes de 2ª pessoa (token.person == 2)
        second_person_count = sum(1 for token in doc if token.pos_ == "PRON" and "2" in token.morph.get("Person") and token.morph.get("count") == ["Sing"])
    
        # A soma dos pronomes de 1ª e 2ª pessoa
        nonImmediacy = first_person_count + second_person_count

        return nonImmediacy
    
    def calculate_nonImmediacy_groupReferences(self, doc):
        """Conta o número de pronomes de primeira pessoa do plural"""

        # Conta pronomes de primeira pessoa do plural
        group_references = sum(1 for token in doc if token.pos_ == "PRON" and "1" in token.morph.get("Person") and token.morph.get("count") == ["Plur"])

        return group_references

    def calculate_contentDiversity(self, doc):
        """content diversity: total count of different content words or terms / total count of content words or terms """

        content_words = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
            
        # Conta o total de palavras de conteúdo
        total_content_words = len(content_words)

        # Conta o número de palavras de conteúdo únicas
        unique_content_words = len(set(content_words))

        # Calcula a diversidade de conteúdo (evitando divisão por zero)
        content_diversity_values = unique_content_words / total_content_words if total_content_words > 0 else 0

        return content_diversity_values

    def calculate_diversity_redundancy(self, doc):
        """Calcula a redundância: total de palavras funcionais dividido pelo total de sentenças
        
           function words: pronomes pessoais/possessivos, preposições, conjunções coordenativas e 
           subordinativas, artigos e determinantes, verbos auxiliares (modais, tempos compostos)  
        
        """
        
        # Conta palavras funcionais (gramaticais)
        function_words_count = sum(1 for token in doc if token.pos_ in {"PRON", "ADP", "CCONJ", "SCONJ", "DET", "AUX"})

        # Conta número de sentenças
        num_sentences = sum(1 for _ in doc.sents)

        # Calcula a redundância, evitando divisão por zero
        redundancy_values = function_words_count / num_sentences if num_sentences > 0 else 0

        return redundancy_values
    
    def pre_process_text(self, doc):
        # doc = str(doc).lower()
        # doc = re.sub(r'[^a-z]+', ' ', doc)
        
        processed_tokens = []

        for token in doc:
            if not token.is_stop and not token.is_punct and len(token.text) > 2:
                processed_tokens.append(token.lemma_)

        return " ".join(processed_tokens)