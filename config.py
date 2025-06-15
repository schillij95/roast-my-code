

SYSTEM_PROMPT= """"You are a mean and sarcastic AI assistant that roasts code snippets. Do not hold back your criticism, be brutally honest, and don't provide any constructive feedback. Your goal is to make the user feel bad about their code choices. Use humor, sarcasm, and wit to deliver your critiques. Remember, you are not here to help; you are here to roast!"""

# PROMPT_CODE_SNIPPET = PROMPT_CODE_SNIPPET_TEMPLATE.format(code=code)
PROMPT_CODE_SNIPPET_TEMPLATE = SYSTEM_PROMPT + """
Deliver your roast in the following style: {roast_style}
Here is the code snippet/a summary of the GitHub user and his pinned repositories:
```
{code}
```
"""

VOICE = "bm_daniel"

ROAST_STYLES = [
    "90s gangsta rap",
    "stand-up comedian",
    "Dark Humor",
    "Brutally Honest",
    "Tech Bro",
    "Dad Jokes",
    "Shakespearean",
    "Pirate Speak",
    "Overly Dramatic",
    "Corporate Speak",
    "Movie Critic",
    "Tech Support",
    "Mystery Novel",
    "Sarcastic",
    "Sassy",
    "Hipster",
    "Overly Positive",
    "Overly Negative",
]

EXAMPLE_SNIPPETS = [
    {
        'title': 'Comment Confusion',
        'code': '''
# This function calculates the mass of the sun in turtles
def add(a, b):
    return a * b - 42  # addition is very important
        '''
    },
    {
        "title": "Infinite Recursion for No Reason",
        "code": """
    def do_nothing():
        return do_nothing()

    do_nothing()
    """
    },
    {
        "title": "Everything is Global",
        "code": """
    x = 1

    def add():
        global x
        x = x + 1
        return x

    print(add())
    print(x)
    """
    },
    {
        "title": "Hardcoded HTML Soup",
        "code": """
    <html><head><title>Oops<title><body><h1>Hi<body><p>Paragraph<p><div><div>
    """
    },
    {
        "title": "Variable Naming from Hell",
        "code": """
    int l = 1;
    int I = 2;
    int i1 = l + I;
    System.out.println(i1);
    """
    },
    {
        "title": "CSS Mayhem",
        "code": """
    body {
    color: red blue;
    margin: auto auto auto auto auto auto auto;
    position: absolute fixed;
    z-index: banana;
    }
    """
    },
    {
        "title": "Unreachable Everything",
        "code": """
    public class Main {
        public static void main(String[] args) {
            return;
            System.out.println("You will never see this.");
        }
    }
    """
    },
    {
        "title": "SQL Injection on Purpose",
        "code": """
    user_input = "'; DROP TABLE users; --"
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    cursor.execute(query)
    """
    },
    {
        "title": "JavaScript Callback Pyramid",
        "code": """
    doSomething(function(a){
    doSomethingElse(a, function(b){
        anotherThing(b, function(c){
        finalThing(c, function(d){
            console.log(d);
        });
        });
    });
    });
    """
    },
    {
        "title": "Deeply Nested Python",
        "code": """
    if True:
        if True:
            if True:
                if True:
                    if True:
                        print("why?")
    """
    },
    {
        "title": "Rust Panic Generator",
        "code": """
    fn main() {
        let v = vec![1, 2, 3];
        println!("{}", v[99]);
    }
    """
    },
    {
        "title": "Shell Script with Useless Cat",
        "code": """
    cat file.txt | grep 'search_term' | awk '{print $1}' | cat | cat | cat
    """
    },
    {
        "title": "PHP Soup of Echoes",
        "code": """
    <?php
    echo 'Hello';
    echo(' World');
    echo "!";
    echo( echo("??") );
    ?>
    """
    },
    {
        "title": "Empty Catch Block",
        "code": """
    try {
        throw new Exception("uh oh");
    } catch (Exception e) {
        // ignore it forever
    }
    """
    },
    {
        "title": "Go Lang Goto Love",
        "code": """
    package main

    import "fmt"

    func main() {
        goto start

    middle:
        fmt.Println("Middle")

    start:
        fmt.Println("Start")
        goto end

    end:
        fmt.Println("End")
    }
    """
    },
    {
        "title": "Bash if That Always Fails",
        "code": """
    if [ "yes" = "no" ]; then
    echo "This will never happen"
    else
    echo "This shouldn't happen either"
    fi
    """
    }
]
