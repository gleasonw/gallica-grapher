


if __name__ == "__main__":
    test_urls = [
        "http://python.org",
        "http://golang.org",
        "http://ruby-lang.org",
    ]
    data = asyncio.run(get(test_urls, on_update_progress=print))
    print("done")
