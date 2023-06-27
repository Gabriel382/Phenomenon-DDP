from lib.ontologyextraction.termenrichment import termEnrichment

class Term():

    def __init__(self, term_name, term_tfidf=None, term_embedding=None, cluster=None, 
                 term_synonims=[],term_hypernyms=[],term_hyponyms=[],term_antonyms=[]):
        self.term_name = term_name
        self.term_embedding = term_embedding
        self.term_tfidf = term_tfidf
        self.cluster = cluster
        self.term_synonyms = term_synonims
        self.term_hypernyms = term_hypernyms
        self.term_hyponyms = term_hyponyms
        self.term_antonyms = term_antonyms
    
    def _Apply_Embedding(self, embeddingFunction):
        self.term_embedding = embeddingFunction(self.term_name)

class Concept():
    def __init__(self, concept_name, list_of_terms, level=1, descriptive_term=None, children_concept=None):
        if descriptive_term is not None:
            assert descriptive_term in list_of_terms
        self.concept_name = concept_name
        self.list_of_terms = list_of_terms
        self.descriptive_term = descriptive_term
        if children_concept is None:
            self.children_concept = []
        else:
            self.children_concept = children_concept
        self.level = level

class Concept_Taxonomy():
    def __init__(self, leaf_concepts=[]):
        self.leaf_concepts=leaf_concepts
        self.deducted_concepts=[]
        self.concept_dict = {}
    
    def createTaxonomyFromDistanceMatrix(self, Z,threshold=None):
        self.deducted_concepts=[]
        self.concept_dict = {}
        for i, merge in enumerate(Z):
            lv1 = 1
            lv2 = 1
            if threshold is not None and threshold < merge[2]:
                continue
            if merge[0] <= len(Z):
                # if it is an original point read it from the centers array
                a = self.leaf_concepts[int(merge[0])]
                lv1 = a.level
            else:
                if int(merge[0]) not in self.concept_dict.keys():
                    continue
                # other wise read the cluster that has been created
                a = self.concept_dict[int(merge[0])]
                lv1 = a.level

            if merge[1] <= len(Z):
                b = self.leaf_concepts[int(merge[1])]
                lv2 = b.level
            else:
                if int(merge[1]) not in self.concept_dict.keys():
                    continue
                b = self.concept_dict[int(merge[1])]
                lv2 = b.level
            # the clusters are 1-indexed by scipy
            newConcept = self._createParentConcept(a,b)
            newConcept.children_concept = list(set(newConcept.children_concept))
            newConcept.list_of_terms = list(set(newConcept.list_of_terms))
            newConcept.level = max(lv1,lv2) + 1
            self.deducted_concepts.append(newConcept)
            self.concept_dict[1 + i + len(Z)] = newConcept

    def _createParentConcept(self,concept1, concept2):
        conceptName = ''
        conceptDT = None
        conceptListOfTerms = concept1.list_of_terms + concept2.list_of_terms
        # Rule 1 - Synonyms
        if self._checkSynonyms(concept1, concept2):
            # print(concept1.concept_name + ' and ' + concept2.concept_name + ' are synonyms')
            if len(concept1.concept_name) == 0 and len(concept2.concept_name) > 0:
                concept2.list_of_terms += concept2.list_of_terms
                concept2.children_concept = concept1.children_concept + concept2.children_concept
                return concept2
            else:
                concept1.list_of_terms += concept2.list_of_terms
                concept1.children_concept = concept1.children_concept + concept2.children_concept
                return concept1

        # Rule 2 - Hypernyms of each other
        concept = self._getParentConcept(concept1,concept2)
        if concept is not None:
            # print(concept1.concept_name + ' and ' + concept2.concept_name + ' are parent and children')
            return concept

        # Rule 3 - Have common Hypernyms
        newTerm = self._commonHypernym(concept1,concept2)
        if newTerm is None:
            # Rule 4 - Head
            newTerm = self._getHead(concept1, concept2)
        if newTerm is not None:
            # print(newTerm.term_name + ' is the parent term of ' + concept1.concept_name + ' and ' + concept2.concept_name)
            newTerm = termEnrichment(newTerm)
            conceptName = newTerm.term_name
            conceptListOfTerms = conceptListOfTerms + [newTerm]
            conceptDT = newTerm
        else:
        # Rule 5 - It's more general
            if (concept1.descriptive_term is None and concept2.descriptive_term is not None)  or (
                (concept1.descriptive_term is not None and concept2.descriptive_term is not None) and 
                (len(concept2.descriptive_term.term_synonyms) > 0 and len(concept1.descriptive_term.term_synonyms)==0)
            ):
                concept2.children_concept = concept2.children_concept + [concept1]
                return concept2
            elif (concept1.descriptive_term is not None and concept2.descriptive_term is None)  or (
                (concept1.descriptive_term is not None and concept2.descriptive_term is not None) and 
                (len(concept2.descriptive_term.term_synonyms) == 0 and len(concept1.descriptive_term.term_synonyms)>0)
            ):
                concept1.children_concept = concept1.children_concept + [concept2]
                return concept1
        
        # Otherwise return blank concept
        concept = Concept(conceptName, conceptListOfTerms
                          ,descriptive_term=conceptDT, children_concept=[concept1,concept2])
        return concept

    def _getHead(self, concept1, concept2):
        c1listterm = []
        c2listterm = []
        for term in concept1.list_of_terms:
            c1listterm = c1listterm + [i.split(' ')[-1].split('-')[-1] for i in term.term_synonyms]
        for term in concept2.list_of_terms:
            c2listterm = c2listterm + [i.split(' ')[-1].split('-')[-1] for i in term.term_synonyms]
        if len(concept1.concept_name) > 0:
            c1listterm.append(concept1.concept_name.lower().split(' ')[-1])
        if len(concept2.concept_name) > 0:
            c2listterm.append(concept2.concept_name.lower().split(' ')[-1])
        for el in c1listterm:
            if el in c2listterm:
                return Term(el)
        return None
        

    def _getParentConcept(self, concept1, concept2):
        if self._checkHyponym(concept1,concept2):
            concept2.children_concept = concept2.children_concept + [concept1]
            return concept2
        elif self._checkHyponym(concept2,concept1):
            concept1.children_concept = concept1.children_concept + [concept2]
            return concept1
        else :
            return None

    def _commonHypernym(self, concept1, concept2):
        c1listterm = []
        c2listterm = []
        for term in concept1.list_of_terms:
            c1listterm =  c1listterm + term.term_hypernyms
        for term in concept2.list_of_terms:
            c2listterm = c2listterm + term.term_hypernyms
        for el in c1listterm:
            if el in c2listterm:
                return Term(el)
        return None

    def _checkHyponym(self, concept1, concept2):
        c1listterm = []
        c2listterm = []
        for term in concept1.list_of_terms:
            c1listterm = c1listterm + term.term_synonyms
        if len(concept1.concept_name) > 0:
            c1listterm.append(concept1.concept_name.lower())
        for term in concept2.list_of_terms:
            c2listterm = c2listterm + term.term_hyponyms
        if len(set(c1listterm).intersection(set(c2listterm))) > 0:
            return True
        else:
            return False
        
    def _checkSynonyms(self, concept1, concept2):
        c1listterm = []
        c2listterm = []
        for term in concept1.list_of_terms:
            c1listterm = c1listterm + term.term_synonyms
        for term in concept2.list_of_terms:
            c2listterm = c2listterm + term.term_synonyms
        if len(concept1.concept_name) > 0:
            c1listterm.append(concept1.concept_name.lower())
        if len(concept2.concept_name) > 0:
            c2listterm.append(concept2.concept_name.lower())
        if len(set(c1listterm).intersection(set(c2listterm))) > 0:
            return True
        else:
            return False