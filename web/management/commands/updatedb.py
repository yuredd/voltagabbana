from django.core.management.base import CommandError, BaseCommand
from web.models import Politician
from SPARQLWrapper import SPARQLWrapper, JSON
import time

class Command(BaseCommand):
    help = 'Updates the politicians list'

#    def add_arguments(self, parser):
#        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS('Requesting lists from Camera dei Deputati.'))

        sparql = SPARQLWrapper("http://dati.camera.it/sparql")
        sparql.setQuery("""

#### deputati in carica: cognome, nome, info biografiche, collegio di elezione, gruppo di appartenenza, commissione di afferenza

SELECT DISTINCT ?persona ?cognome ?nome 
?dataNascita  ?nato ?luogoNascita ?genere 
# ?collegio ?nomeGruppo ?sigla ?commissione ?aggiornamento  
?collegio ?nomeGruppo ?sigla ?aggiornamento  
WHERE {
?persona ocd:rif_mandatoCamera ?mandato; a foaf:Person.

## deputato
?d a ocd:deputato; ocd:aderisce ?aderisce;
ocd:rif_leg <http://dati.camera.it/ocd/legislatura.rdf/repubblica_17>;
ocd:rif_mandatoCamera ?mandato.

## anagrafica
?d foaf:surname ?cognome; foaf:gender ?genere;foaf:firstName ?nome.
OPTIONAL{
?persona <http://purl.org/vocab/bio/0.1/Birth> ?nascita.
?nascita <http://purl.org/vocab/bio/0.1/date> ?dataNascita; 
rdfs:label ?nato; ocd:rif_luogo ?luogoNascitaUri. 
?luogoNascitaUri dc:title ?luogoNascita. 
}

## aggiornamento del sistema
OPTIONAL{?d <http://lod.xdams.org/ontologies/ods/modified> ?aggiornamento.}

## mandato
?mandato ocd:rif_elezione ?elezione.  
MINUS{?mandato ocd:endDate ?fineMandato.}

## elezione
?elezione dc:coverage ?collegio.

## adesione a gruppo
OPTIONAL{
  ?aderisce ocd:rif_gruppoParlamentare ?gruppo.
  ?gruppo <http://purl.org/dc/terms/alternative> ?sigla.
  ?gruppo dc:title ?nomeGruppo.
}

MINUS{?aderisce ocd:endDate ?fineAdesione}

## organo
?d ocd:membro ?membro.?membro ocd:rif_organo ?organo. 
?organo dc:title ?commissione .
MINUS{?membro ocd:endDate ?fineMembership}
}

        """)
        sparql.setReturnFormat(JSON)
        results_camera = sparql.query().convert()

        self.stdout.write(self.style.SUCCESS('Finished request from Camera dei Deputati.'))
        self.stdout.write(self.style.SUCCESS('Requesting lists from Camera del Senato.'))


        sparql = SPARQLWrapper("http://dati.senato.it/sparql")
        sparql.setQuery("""
PREFIX ocd: <http://dati.camera.it/ocd/>
PREFIX osr: <http://dati.senato.it/osr/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?nome ?cognome ?sigla ?senatore ?carica ?inizioAdesione
WHERE
{
    ?gruppo a ocd:gruppoParlamentare .
    ?gruppo osr:denominazione ?denominazione .
    ?denominazione osr:titolo ?nomeGruppo .
    ?denominazione osr:titoloBreve ?sigla .
    ?adesioneGruppo a ocd:adesioneGruppo .
    ?adesioneGruppo osr:carica ?carica .
    ?adesioneGruppo osr:inizio ?inizioAdesione.
    ?adesioneGruppo osr:gruppo ?gruppo.
    ?senatore ocd:aderisce ?adesioneGruppo.
    ?senatore a osr:Senatore.
    ?senatore foaf:firstName ?nome.
    ?senatore foaf:lastName ?cognome.
    OPTIONAL { ?adesioneGruppo osr:fine ?fineAdesione }
    OPTIONAL { ?denominazione osr:fine ?fineDenominazione }
    FILTER(!bound(?fineAdesione) && !bound(?fineDenominazione) )
}

        """)
        sparql.setReturnFormat(JSON)
        results_senato = sparql.query().convert()

        self.stdout.write(self.style.SUCCESS('Finished request from Camera del Senato.'))

        self.stdout.write(self.style.SUCCESS('Persisting requested data.'))

        Politician.objects.all().update(present=False)

        for result in results_camera["results"]["bindings"]:
#            print(result["cognome"]["value"] + " " + result["sigla"]["value"])

# ?persona ?cognome ?nome 
# ?dataNascita  ?nato ?luogoNascita ?genere 
# ?collegio ?nomeGruppo ?sigla ?aggiornamento  

            politician, created = Politician.objects.get_or_create(
             name = result["nome"]["value"], surname = result["cognome"]["value"],
             defaults = {
              'present':True,
              'area':'camera',
              'name':result["nome"]["value"],
              'surname':result["cognome"]["value"],
              'gender':result["genere"]["value"],
              'group':result["sigla"]["value"],
              'dateOfBirth':time.strftime('%Y-%m-%d', time.localtime(int(result["dataNascita"]["value"] + "0"))),
              'dateUpdate':result["aggiornamento"]["value"][:10],
              'placeOfBirth':result["luogoNascita"]["value"],
             }
            )

            if(not created):
                if(politician.group != result["sigla"]["value"]):
                    print("Il deputato {} {} ha cambiato da {} a {}.".format(result["cognome"]["value"], result["nome"]["value"], politician.group, result["sigla"]["value"]))

                politician, created = Politician.objects.update_or_create(
                 name = result["nome"]["value"], surname = result["cognome"]["value"],
                 defaults = {
                  'present':True,
                  'area':'camera',
                  'name':result["nome"]["value"],
                  'surname':result["cognome"]["value"],
                  'gender':result["genere"]["value"],
                  'group':result["sigla"]["value"],
                  'dateOfBirth':time.strftime('%Y-%m-%d', time.localtime(int(result["dataNascita"]["value"] + "0"))),
                  'dateUpdate':result["aggiornamento"]["value"][:10],
                  'placeOfBirth':result["luogoNascita"]["value"],
                 }
                )

        self.stdout.write(self.style.SUCCESS('Successfully persisted Camera data, %s rows returned.' % len(results_camera["results"]["bindings"])))

        self.stdout.write(self.style.SUCCESS('Persisting requested data.'))

        for result in results_senato["results"]["bindings"]:
#            print(result["cognome"]["value"] + " " + result["sigla"]["value"])

# ?persona ?cognome ?nome 
# ?dataNascita  ?nato ?luogoNascita ?genere 
# ?collegio ?nomeGruppo ?sigla ?aggiornamento  

            politician, created = Politician.objects.get_or_create(
             name = result["nome"]["value"], surname = result["cognome"]["value"],
             defaults = {
              'present':True,
              'area':'senato',
              'name':result["nome"]["value"],
              'surname':result["cognome"]["value"],
#              'gender':result["genere"]["value"],
              'group':result["sigla"]["value"],
#              'dateOfBirth':time.strftime('%Y-%m-%d', time.localtime(int(result["dataNascita"]["value"] + "0"))),
#              'dateUpdate':result["aggiornamento"]["value"][:10],
#              'placeOfBirth':result["luogoNascita"]["value"],
             }
            )

            if(not created):
                if(politician.group != result["sigla"]["value"]):
                    print("Il senatore {} {} ha cambiato da {} a {}.".format(result["cognome"]["value"], result["nome"]["value"], politician.group, result["sigla"]["value"]))

                politician, created = Politician.objects.update_or_create(
                 name = result["nome"]["value"], surname = result["cognome"]["value"],
                 defaults = {
                  'present':True,
                  'area':'senato',
                  'name':result["nome"]["value"],
                  'surname':result["cognome"]["value"],
#                  'gender':result["genere"]["value"],
                  'group':result["sigla"]["value"],
#                  'dateOfBirth':time.strftime('%Y-%m-%d', time.localtime(int(result["dataNascita"]["value"] + "0"))),
#                  'dateUpdate':result["aggiornamento"]["value"][:10],
#                  'placeOfBirth':result["luogoNascita"]["value"],
                 }
                )

        self.stdout.write(self.style.SUCCESS('Successfully persisted Senato data, %s rows returned.' % len(results_senato["results"]["bindings"])))

        Politician.objects.filter(present=False).delete()

