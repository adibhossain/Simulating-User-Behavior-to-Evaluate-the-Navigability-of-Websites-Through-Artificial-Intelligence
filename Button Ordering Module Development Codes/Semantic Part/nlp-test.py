from sentence_transformers import SentenceTransformer, util

def semantic_similarity(sentence1, sentence2, model_name="paraphrase-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)

    embeddings1 = model.encode(sentence1, convert_to_tensor=True)
    embeddings2 = model.encode(sentence2, convert_to_tensor=True)

    similarity_score = util.pytorch_cos_sim(embeddings1, embeddings2)[0][0].item()

    return similarity_score

sentence1 = "Dawn"
sentence2 = "Midnight"
sentence3 = ""

# sentence1 = "rivers woods and hills"
# sentence2 = "streams forests and mountains"
# sentence3 = "deserts sand and shrubs"

similarity_score = semantic_similarity(sentence1, sentence2)

print(f"Semantic similarity between '{sentence1}' and '{sentence2}': {similarity_score}")

similarity_score = semantic_similarity(sentence1, sentence3)

print(f"Semantic similarity between '{sentence1}' and '{sentence3}': {similarity_score}")

similarity_score = semantic_similarity(sentence2, sentence3)

print(f"Semantic similarity between '{sentence2}' and '{sentence3}': {similarity_score}")
