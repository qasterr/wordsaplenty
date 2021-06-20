import requests
from sys import exit
from json import loads
from bs4 import BeautifulSoup
import click
from rich.console import Console

console = Console()

# Override the default print method
print = console.print


def _find_value(input_, key, value):
    for item in input_:
        if item.get(key) == value:
            return item


def _status_code(req):
    if req.status_code != 200:
        print("[bold red]Error during request.[/]", "Status code:", req.status_code)
        quit()
    

def _invalid_word_type(word, word_type):
    print(f"[bold red]{word} is not a(n) {word_type}[/]")
    quit()


def _print_definition(word: str, word_type: str, definitions: list):
    
    def format_spaces(items, start=1):
        length = len(items) + start
        return " " * length
        
    def limit_list(list_, n) -> str:
        ret = ""
        for i, item in enumerate(list_):
            if i <= n:
                ret += f"[white]{item}, [/]"
            else:
                ret += f"[white]{item}...[/]"
                break
        return ret
        
    print(f"[bold cyan]{word}[/] [italic]{word_type}[/]")
    for i, definition in enumerate(definitions["definitions"], start=1):
        print("\t" + f"[bold cyan]{i}.[/] {definition['definition']}")
        if "synonyms" in definition:
            print("\t" + format_spaces(definitions) + f"[bold cyan]Synonyms: [/][italics]{limit_list(definition['synonyms'], 3)}[/]")
        print("")


def dictionary_api(word, word_type, language, **kwargs):
    
    url = f"https://api.dictionaryapi.dev/api/v2/entries/{language}/{word}"
    
    req = requests.get(url)
    
    _status_code(req)
    
    content = loads(req.content)[0]
    
    definitions = _find_value(content["meanings"], "partOfSpeech", word_type)
    
    if definitions is None:
        _invalid_word_type(word, word_type)
        
    _print_definition(word, definitions["partOfSpeech"], definitions)


@click.command()
@click.argument("word", type=str, nargs=-1)
@click.option("--type_", "--type", "-t", type=str, default="noun")
@click.option("--dictionary", "-d", "--dict", type=str, default="dictionary_api")
@click.option("--language", "-l", "--lang", type=str, default="en_GB")
def main(word, type_, dictionary, language):
    
    # For adding future dictionaries
    dictionaries = {
        "dictionary_api": dictionary_api,
    }
    
    word = " ".join(word)
        
    
    def default(*args):
        print(f"[bold red]Invalid dictionary.[/] Valid dictionaries are: ", [key for key in dictionaries.keys()])
    
    type_ = type_.lower()
    if type_ in ('n', 'noun'):
        type_ = "noun"
    elif type_ in ('v', 'verb'):
        type_ = "verb"
    elif type_ in ('a', 'adj', 'adjective'):
        type_ = "adjective"
    elif type_ in ('adv', 'adverb'):
        type_ = "adverb"
    
    
    dictionaries.get(dictionary.lower(), default)(word, type_, language)


if __name__ == '__main__':
    main()
