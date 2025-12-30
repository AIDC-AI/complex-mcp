import Levenshtein

def lev_sim(x: str, y: str):
    dist = Levenshtein.distance(x, y)

    return 1 - dist / max(len(x), len(y))


if __name__ == "__main__":
    
    x = "hello, world!"
    y = "hello, word!"

    print(lev_sim(x, y))
