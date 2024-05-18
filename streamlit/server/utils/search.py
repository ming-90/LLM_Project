import pandas as pd

def query2docs(collection, search_text,max_results, client, encoder):
    docs = []
    all_hits = []
    collection_name = f"{collection}"
    hits = client.search(
        collection_name=collection_name,
        query_vector=encoder.encode(search_text).tolist(),
        limit=max_results
    )
    all_hits.extend(hits)

    sorted_hits = sorted(all_hits, key=lambda x: x.score, reverse=True)
    if collection == "OCR":
        for hit in sorted_hits:
            t = str(hit.payload["time"]).split('.')[0]
            doc = {
                "score":hit.score,
                "text":hit.payload['text'],
                "time": t
            }
            docs.append(doc)

    dataFrame = pd.DataFrame.from_dict(docs)

    print(dataFrame)

    return dataFrame