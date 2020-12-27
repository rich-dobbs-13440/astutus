import astutus.util


def test_print():
    ansi = astutus.util.AnsiSequenceStack()
    print(f"Base text {ansi.push('red')}red test{ansi.pop()} more base text")


def test_print_nested():
    ansi = astutus.util.AnsiSequenceStack()
    print(f"Base text {ansi.push('blue')} some blue text "
          f"{ansi.push('red')}red test{ansi.pop()} "
          f"some more blue text  {ansi.pop()} more base text")


def test_print_more_concise():
    ansi = astutus.util.AnsiSequenceStack()
    start = ansi.push
    end = ansi.end
    print(f"Base text {start('blue')} some blue text "
          f"{start('red')}red test{end('red')} "
          f"some more blue text  {end('blue')} more base text")
