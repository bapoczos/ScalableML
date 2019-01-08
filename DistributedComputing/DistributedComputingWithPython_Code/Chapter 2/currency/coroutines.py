def coroutine(fn):
    def wrapper(*args, **kwargs):
        c = fn(*args, **kwargs)
        next(c)
        return c
    return wrapper


def complain_about(substring):
    print('Please talk to me!')
    try:
        while True:
            text = (yield)
            if substring in text:
                print('Oh no: I found a %s again!'
                      % (substring))
    except GeneratorExit:
        print('Ok, ok: I am quitting.')


@coroutine
def complain_about2(substring):
    print('Please talk to me!')
    while True:
        text = (yield)
        if substring in text:
            print('Oh no: I found a %s again!'
                  % (substring))


if __name__ == '__main__':
    c = complain_about('Ruby')
    next(c)
    c.send('Test data')
    c.send('Some more random text')
    c.send('Test data with Ruby somewhere in it')
    c.send('Stop complaining about Ruby or else!')
    c.close()

    c = complain_about2('JavaScript')
    c.send('Test data')
    c.send('Some more random text')
    c.send('Test data with JavaScript somewhere in it')
    c.send('Stop complaining about JavaScript or else!')
    c.close()
