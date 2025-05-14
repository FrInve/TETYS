from collections import defaultdict

K_ELEMENTS = 3

ranking1 = [('skk', 12), ('eskere', 10), ('palla', 8), ('carciofo', 6), ('cozza', 2)]
ranking2 = [('skk', 12), ('palla', 10), ('cozza', 8), ('salame', 6), ('prosciutto', 2)]
ranking3 = [('eskere', 12), ('palla', 10), ('salame', 8), ('borraccia', 6), ('carciofo', 2)]

list_of_rankings = [ranking1, ranking2, ranking3]

# plurality score computation
def plurality_score(list_of_rankings):
	first_places = defaultdict(int)
	for rank in list_of_rankings:
		if rank:
			candidate = rank[0][0]  # get candidate name from the first position
			first_places[candidate] += 1
	return dict(first_places)

# update the ranking
def update_ranking(first_places, final_ranking):
	winner = max(first_places.items(), key=lambda x: x[1])[0]
	final_ranking.append(winner)

	# remove winner from rankings
	for rank in list_of_rankings:
		rank[:] = [entry for entry in rank if entry[0] != winner]

if __name__ == "__main__":
	final_ranking = []
	for k in range(K_ELEMENTS):
		first_places = plurality_score(list_of_rankings)
		update_ranking(first_places, final_ranking)
	print(final_ranking)
