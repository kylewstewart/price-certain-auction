import locale

class Orders(object):
	def __init__(self, mkt_data):
		self.mkt_data = mkt_data
		self.bid_id = int()
		self.offer_id = int()
		self.bids = dict()
		self.offers = dict()

	def add_bid(self, vol, limit, target, price_liquidity, min_vol):

		vol = int(vol)
		limit = float(limit)
		price_liquidity = int(price_liquidity)
		min_vol = int(min_vol)
		bid = self.mkt_data.get_best_bid()
		offer = self.mkt_data.get_best_offer()

		self.bid_id += 1

		bid_list = list()
		bid_list.append(vol)

		if target == "bid" and bid <= limit:
			bid_list.append(bid)
		elif target == "offer" and offer <= limit:
			bid_list.append(offer)
		else:
			bid_list.append(limit)

		bid_list.append(price_liquidity)
		bid_list.append(min_vol)

		self.bids[self.bid_id] = bid_list

		return self.bid_id

	def modify_bid(self, bid_id, price, vol):
		price = float(price)
		vol = int(vol)
		bid_list = list()

		bid_list.append(bid_id)
		bid_list.append(price)
		bid_list.append(vol)

		for i in self.bids:
			if bid_id in self.bids[i]:
				self.bids[i] = bid_list
				break

	def delete_bid(self, bid_id):
		for i in self.bids:
			if bid_id in self.bids[i]:
				del self.bids[i]
				break

	def get_bids(self):

		return self.bids

	def add_offer(self, vol, limit, target, price_liquidity, min_vol):

		vol = int(vol)
		limit = float(limit)
		price_liquidity = int(price_liquidity)
		min_vol = int(min_vol)
		bid = self.mkt_data.get_best_bid()
		offer = self.mkt_data.get_best_offer()

		self.offer_id += 1

		offer_list = list()
		offer_list.append(vol)

		if target == "bid" and bid >= limit:
			offer_list.append(bid)
		elif target == "offer" and offer >= limit:
			offer_list.append(offer)
		else:
			offer_list.append(limit)

		offer_list.append(price_liquidity)
		offer_list.append(min_vol)

		self.offers[self.offer_id] = offer_list

		return self.offer_id

	def modify_offer(self, offer_id, price, vol):
		price = float(price)
		vol = int(vol)
		offer_list = list()

		offer_list.append(offer_id)
		offer_list.append(price)
		offer_list.append(vol)

		for i in self.offers:
			if offer_id in self.offers[i]:
				self.offers[i] = offer_list
				break

	def delete_offer(self, offer_id):
		for i in self.offers:
			if offer_id in self.offers[i]:
				del self.offers[i]
				break

	def get_offers(self):

		return self.offers

	def random_bids(self, max_bids, max_vol):
		import random
		num_bids = random.randint(1, max_bids)
		prices = self.mkt_data.get_prices()

		for i in range(1, num_bids + 1):
			vol = random.randint(1, (max_vol / 10000)) * 10000
			limit = random.choice(prices)
			target = 0
			price_liquidity = 3
			min_vol = float(random.randint(5, 20))
			min_vol = int((min_vol / 100) * vol)

			self.add_bid(vol, limit, target, price_liquidity, min_vol)

	def random_offers(self, max_offers, max_vol):
		import random
		num_offers = random.randint(1, max_offers)
		prices = self.mkt_data.get_prices()

		for i in range(1, num_offers + 1):
			vol = random.randint(1, (max_vol / 10000)) * 10000
			limit = random.choice(prices)
			target = 0
			price_liquidity = 3
			min_vol = float(random.randint(20, 40))
			min_vol = int((min_vol / 100) * vol)

			self.add_offer(vol, limit, target, price_liquidity, min_vol)


class MktData(object):
	def __init__(self, best_bid, best_bid_size, best_offer, best_offer_size, spread, tp, round_lot):

		self.best_bid = best_bid
		self.best_bid_size = best_bid_size
		self.best_offer = best_offer
		self.best_offer_size = best_offer_size
		self.spread = spread
		self.tp = tp
		self.round_lot = round_lot

	def get_prices(self):
		prices = list()
		tp = self.tp
		best_bid = self.best_bid
		best_offer = self.best_offer
		spread = self.spread

		if tp % 2 is not 0:
			tp -= 1

		prices.append(best_bid)
		prices.append(best_offer)
		prices.append(self.get_mid_point())

		counter = 1

		while counter < int((tp/2)):

			offer_price = round(best_offer + (counter * spread), 4)
			bid_price = round(best_bid - (counter * spread), 4)

			prices.append(offer_price)
			prices.append(bid_price)

			counter += 1

		return prices

	def mkt_bid_vols(self):
		import math
		bid_vol = self.best_bid_size
		mkt_bid_vols = dict()

		adj = 1 - math.log(3, 10)

		counter = 0
		for price in sorted(self.get_prices(), reverse=True):
			if price == self.best_bid:
				mkt_bid_vols[price] = bid_vol
			if price < self.best_bid:
				counter += 1
				if counter == 1:
					bid_vol = int(1.5 * bid_vol)
					mkt_bid_vols[price] = bid_vol
				else:
					bid_vol = int(adj * bid_vol)
					mkt_bid_vols[price] = bid_vol

		return mkt_bid_vols

	def cum_mkt_bid_vol(self, price):
		mkt_bid_vols = self.mkt_bid_vols()
		cum_mkt_bid_vol = dict()

		if mkt_bid_vols.get(price):
			cum_bid = int()
			for p in sorted(self.get_prices(), reverse= True):
				if p <= self.best_bid:
					cum_bid += mkt_bid_vols[p]
					cum_mkt_bid_vol[p] = cum_bid
			return cum_mkt_bid_vol[price]
		else:
			return 0

	def mkt_offer_vols(self):
		import math
		offer_vol = self.best_offer_size
		mkt_offer_vols = dict()

		adj = 1 - math.log(3, 10)

		counter = 0
		for price in sorted(self.get_prices()):
			if price == self.best_offer:
				mkt_offer_vols[price] = offer_vol
			if price > self.best_offer:
				counter += 1
				if counter ==1:
					offer_vol = int(1.5 * offer_vol)
					mkt_offer_vols[price] = offer_vol
				else:
					offer_vol = int(adj * offer_vol)
					mkt_offer_vols[price] = offer_vol

		return mkt_offer_vols

	def cum_mkt_offer_vol(self, price):
		mkt_offer_vols = self.mkt_offer_vols()
		cum_mkt_offer_vol = dict()

		if mkt_offer_vols.get(price):
			cum_offer = int()
			for p in sorted(self.get_prices()):
				if p >= self.best_offer:
					cum_offer += mkt_offer_vols[p]
					cum_mkt_offer_vol[p] = cum_offer
			return cum_mkt_offer_vol[price]
		else:
			return 0

	def get_best_bid(self):

		return self.best_bid

	def get_best_bid_size(self):

		return self.best_bid_size

	def get_best_offer(self):

		return self.best_offer

	def get_best_offer_size(self):

		return self.best_offer_size

	def get_mid_point(self):

		mid_point = round((self.best_bid + self.best_offer) / float(2), 4)

		return mid_point

	def get_spread(self):

		return self.spread

	def get_tp(self):

		return self.tp

	def get_round_lot(self):

		return self.round_lot


class Market(object):
	def __init__(self, orders, mkt_data, bids_at_price, offers_at_price):
		self.orders = orders
		self.mkt_data = mkt_data
		self.bids_at_price = bids_at_price
		self.offers_at_price = offers_at_price

	def bid_dap(self, price):
		bids = self.orders.get_bids()

		dap = 0
		for bid_id in bids:

			dap_dict = self.bids_at_price[bid_id]
			dap += dap_dict[price]

		dap += self.mkt_data.cum_mkt_bid_vol(price)

		return dap

	def offer_dap(self, price):
		offers = self.orders.get_offers()

		dap = 0
		for offer_id in offers:
			dap_dict = self.offers_at_price[offer_id]

			dap += dap_dict[price]

		dap += self.mkt_data.cum_mkt_offer_vol(price)

		return dap

	def bid_guap(self, price):
		mkt_bid_vols = self.mkt_data.mkt_bid_vols()
		bid_guap = int()

		for p in mkt_bid_vols:
			if p > price:
				bid_guap += mkt_bid_vols[p]

		if self.offer_dap(price) > self.bid_dap(price):
			bid_guap -= min(bid_guap, self.offer_dap(price) - self.bid_dap(price))

		return bid_guap

	def offer_guap(self, price):
		mkt_offer_vols = self.mkt_data.mkt_offer_vols()
		offer_guap = int()

		for p in mkt_offer_vols:
			if p < price:
				offer_guap += mkt_offer_vols[p]

		if self.bid_dap(price) > self.avap(price):
			offer_guap -= min(offer_guap, self.bid_dap(price) - self.avap(price))

		return offer_guap

	def avap(self, price):

		if self.offer_dap(price) <= self.bid_dap(price):
			return self.offer_dap(price)

		elif self.bid_dap(price) < self.offer_dap(price):
			return self.bid_dap(price)

	def bid_avap(self, price):
		if self.avap(price) - self.bid_guap(price) < 0:
			return 0
		else:
			return self.avap(price) - self.bid_guap(price)

	def offer_avap(self, price):
		if self.avap(price) - self.offer_guap(price) < 0:
			return 0
		else:
			return self.avap(price) - self.offer_guap(price)

	def bid_alloc(self, bid_id, price):
		bids_at_price = self.bids_at_price
		bid_vols = dict()

		for buyer in bids_at_price:
			bid_vols[buyer] = bids_at_price[buyer][price]

		if bid_vols.get(bid_id) is None:
			return 0
		elif self.bid_avap(price) == 0:
			return 0
		elif self.bid_dap(price) <= self.bid_avap(price):
			return bid_vols[bid_id]
		elif bid_vols[bid_id] <= self.bid_avap(price) / len(bid_vols):
			return bid_vols[bid_id]
		else:
			alloc = int(self.bid_avap(price))
			alloc_dict = dict()
			balance_dict = dict()

			for buyer in bid_vols:
				alloc_dict[buyer] = 0
				balance_dict[buyer] = bid_vols[buyer]

			while alloc > 0:
				for buyer in bid_vols:
					if balance_dict[buyer] <= alloc / len(bid_vols):
						alloc_dict[buyer] += balance_dict[buyer]
						balance_dict[buyer] = 0
					elif balance_dict[buyer] > alloc / len(bid_vols):
						alloc_dict[buyer] += alloc / len(bid_vols)
						balance_dict[buyer] -= alloc / len(bid_vols)

				cum_alloc = int()
				for buyer in alloc_dict:
					cum_alloc += alloc_dict[buyer]
					if bid_vols.get(buyer) is None:
						pass
					elif alloc_dict[buyer] == bid_vols[buyer]:
						if buyer in bid_vols:
							del bid_vols[buyer]

				alloc = self.bid_avap(price) - cum_alloc

				if 0 < alloc < len(bid_vols):
					for i in range(1, alloc + 1):
						import random

						x = random.choice(bid_vols.keys())
						alloc_dict[x] += 1

			return alloc_dict[bid_id]

	def offer_alloc(self, offer_id, price):
		offers_at_price = self.offers_at_price
		offer_vols = dict()

		for seller in offers_at_price:
			offer_vols[seller] = offers_at_price[seller][price]

		if offer_vols.get(offer_id) is None:
			return 0
		elif self.offer_avap(price) == 0:
			return 0
		elif self.offer_dap(price) <= self.offer_avap(price):
			return offer_vols[offer_id]
		elif offer_vols[offer_id] <= self.offer_avap(price) / len(offer_vols):
			return offer_vols[offer_id]
		else:
			alloc = int(self.offer_avap(price))
			alloc_dict = dict()
			balance_dict = dict()

			for seller in offer_vols:
				alloc_dict[seller] = 0
				balance_dict[seller] = offer_vols[seller]

			while alloc > 0:
				for seller in offer_vols:
					if balance_dict[seller] <= alloc / len(offer_vols):
						alloc_dict[seller] += balance_dict[seller]
						balance_dict[seller] = 0
					elif balance_dict[seller] > alloc / len(offer_vols):
						alloc_dict[seller] += alloc / len(offer_vols)
						balance_dict[seller] -= alloc / len(offer_vols)

				cum_alloc = int()
				for seller in alloc_dict:
					cum_alloc += alloc_dict[seller]
					if offer_vols.get(seller) is None:
						pass
					elif alloc_dict[seller] == offer_vols[seller]:
						if seller in offer_vols:
							del offer_vols[seller]

				alloc = self.offer_avap(price) - cum_alloc

				if 0 < alloc < len(offer_vols):
					for i in range(1, alloc + 1):
						import random

						x = random.choice(offer_vols.keys())
						alloc_dict[x] += 1

			return alloc_dict[offer_id]


class Utility(object):
	def __init__(self, orders, mkt_data):
		self.orders = orders
		self.mkt_data = mkt_data

	def bid_pu(self, bid_id, price):
		bids = self.orders.get_bids()
		limit = bids[bid_id][1]
		prices = self.mkt_data.get_prices()

		max_price = max(prices)
		min_price = min(prices) - self.mkt_data.get_spread()

		u = 10 / (max_price - min_price)

		if price <= limit:
			return 11 - (u * (price - min_price))

		else:
			return 0

	def bid_vu(self, bid_id, vol):
		bids = self.orders.get_bids()
		order_vol = float(bids[bid_id][0])

		vol = float(vol)
		vu = (vol / order_vol) * 1000
		vu = int(vu)

		deci = float(vu % 100) / 100
		vu /= 100
		vu = float(vu)
		vu += deci

		if vu > 10:
			return 10
		else:
			return vu

	def bid_min_vol_at_price(self, bid_id, price):
		bids = self.orders.get_bids()
		best_offer = self.mkt_data.get_best_offer()
		mid = self.mkt_data.get_mid_point()
		min_vol = bids[bid_id][3]
		lmt = bids[bid_id][1]

		if price < best_offer:
			min_vol_at_price = 0
		elif price > lmt:
			min_vol_at_price = 0
		else:
			min_vol_at_price = ((min_vol / (best_offer - mid)) * price) - ((min_vol / (best_offer - mid)) * mid)

		return min_vol_at_price

	def bid_signal(self, bid_id, price):
		best_offer = self.mkt_data.get_best_offer()
		round_lot = self.mkt_data.get_round_lot()
		min_vol_at_price = self.bid_min_vol_at_price(bid_id, price)

		if price < best_offer:
			signal = 0
		elif min_vol_at_price == 0:
			signal = 0
		else:
			signal = self.bid_pu(bid_id, price) * self.bid_vu(bid_id, min_vol_at_price - round_lot)

		return signal

	def bid_eu(self, bid_id, price, vol):
		cum_mkt_offer_vol = self.mkt_data.cum_mkt_offer_vol(price)
		pu = self.bid_pu(bid_id, price)
		vu = self.bid_vu(bid_id, vol)
		signal = self.bid_signal(bid_id, price)

		if pu == 0 or vu == 0:
			eu = 0
		elif (pu * vu) - signal < 0:
			eu = 0
		# elif vol <= cum_mkt_offer_vol:
		#     eu = 0
		else:
			eu = (pu * vu) - signal

		return eu

	def base_bids_at_price(self):
		bids = self.orders.get_bids()
		prices = self.mkt_data.get_prices()

		dap = dict()
		for bid_id in bids:
			dap[bid_id] = 0

		for bid_id in bids:
			bap = dict()
			for price in prices:
				bap[price] = 0
			for price in prices:
				if bids[bid_id][1] >= price:
					bap[price] += bids[bid_id][0]
			dap[bid_id] = bap

		return dap

	def pos_max_util_bids_at_price(self):
		bids = self.orders.get_bids()
		prices = self.mkt_data.get_prices()
		base = Market(self.orders, self.mkt_data, self.base_bids_at_price(), self.base_offers_at_price())

		dap = dict()
		for bid_id in bids:
			dap[bid_id] = 0
		for bid_id in bids:
			bap = dict()
			for price in prices:
				bap[price] = 0
			for price in sorted(prices, reverse= True):
				order_vol = bids[bid_id][0]
				bid_avap = base.bid_avap(price)
				if bid_avap >= order_vol:
					vol = order_vol
				else:
					vol = bid_avap
				if self.bid_eu(bid_id, price, vol) > 0:
					bap[price] += bids[bid_id][0]
			dap[bid_id] = bap

		return dap

	def pos_min_util_bids_at_price(self):
		bids = self.orders.get_bids()
		prices = self.mkt_data.get_prices()
		pos_max_util = Market(self.orders, self.mkt_data, self.pos_max_util_bids_at_price(), self.pos_max_util_offers_at_price())

		dap = dict()
		for bid_id in bids:
			dap[bid_id] = 0
		for bid_id in bids:
			bap = dict()
			for price in prices:
				bap[price] = 0
			for price in prices:
				vol = pos_max_util.bid_alloc(bid_id, price)
				if self.bid_eu(bid_id, price, vol) > 0:
					bap[price] += bids[bid_id][0]
			dap[bid_id] = bap

		return dap

	def offer_pu(self, offer_id, price):
		offers = self.orders.get_offers()
		limit = offers[offer_id][1]
		prices = self.mkt_data.get_prices()
		tp = self.mkt_data.get_tp()

		max_price = max(prices)
		min_price = min(prices) - self.mkt_data.get_spread()

		u = 10 / (max_price - min_price)

		if price >= limit:
			return u * (price - min_price)

		else:
			return 0

	def offer_vu(self, offer_id, vol):
		offers = self.orders.get_offers()
		order_vol = float(offers[offer_id][0])

		vol = float(vol)
		vu = (vol / order_vol) * 1000
		vu = int(vu)

		deci = float(vu % 100) / 100
		vu /= 100
		vu = float(vu)
		vu += deci

		if vu > 10:
			return 10
		else:
			return vu

	def offer_min_vol_at_price(self, offer_id, price):
		offers = self.orders.get_offers()
		best_bid = self.mkt_data.get_best_bid()
		mid = self.mkt_data.get_mid_point()
		min_vol = offers[offer_id][3]
		lmt = offers[offer_id][1]

		if price > best_bid:
			min_vol_at_price = 0
		elif price < lmt:
			min_vol_at_price = 0
		else:
			min_vol_at_price = ((min_vol / (best_bid - mid)) * price) - ((min_vol / (best_bid - mid)) * mid)

		return min_vol_at_price

	def offer_signal(self, offer_id, price):
		best_bid = self.mkt_data.get_best_bid()
		round_lot = self.mkt_data.get_round_lot()
		min_vol_at_price = self.offer_min_vol_at_price(offer_id, price)

		if price > best_bid:
			signal = 0
		elif min_vol_at_price == 0:
			signal = 0
		else:
			signal = self.offer_pu(offer_id, price) * self.offer_vu(offer_id, min_vol_at_price - round_lot)

		return signal

	def offer_eu(self, offer_id, price, vol):
		cum_mkt_bid_vol = self.mkt_data.cum_mkt_bid_vol(price)
		pu = self.offer_pu(offer_id, price)
		vu = self.offer_vu(offer_id, vol)
		signal = self.offer_signal(offer_id, price)

		if pu == 0 or vu == 0:
			eu = 0
		elif (pu * vu) - signal < 0:
			eu = 0
		# elif vol <= cum_mkt_bid_vol:
		#     eu = 0
		else:
			eu = (vu * pu) - signal

		return eu

	def base_offers_at_price(self):
		offers = self.orders.get_offers()
		prices = self.mkt_data.get_prices()


		dap = dict()
		for offer_id in offers:
			dap[offer_id] = 0
		for offer_id in offers:
			oap = dict()
			for price in prices:
				oap[price] = 0
			for price in prices:
				if offers[offer_id][1] <= price:
					oap[price] += offers[offer_id][0]

			dap[offer_id] = oap

		return dap

	def pos_max_util_offers_at_price(self):
		offers = self.orders.get_offers()
		prices = self.mkt_data.get_prices()
		base = Market(self.orders, self.mkt_data, self.base_bids_at_price(), self.base_offers_at_price())

		dap = dict()
		for offer_id in offers:
			dap[offer_id] = 0
		for offer_id in offers:
			oap = dict()
			for price in prices:
				oap[price] = 0
			for price in prices:
				order_vol = offers[offer_id][0]
				offer_avap = base.offer_avap(price)
				if offer_avap >= order_vol:
					vol = order_vol
				else:
					vol = offer_avap
				if self.offer_eu(offer_id, price, vol) > 0:
					oap[price] += offers[offer_id][0]
			dap[offer_id] = oap

		return dap

	def pos_min_util_offers_at_price(self):
		offers = self.orders.get_offers()
		prices = self.mkt_data.get_prices()
		pos_max_util = Market(self.orders, self.mkt_data, self.pos_max_util_bids_at_price(),
							  self.pos_max_util_offers_at_price())

		dap = dict()
		for offer_id in offers:
			dap[offer_id] = 0
		for offer_id in offers:
			oap = dict()
			for price in prices:
				oap[price] = 0
			for price in prices:
				vol = pos_max_util.offer_alloc(offer_id, price)
				if self.offer_eu(offer_id, price, vol) > 0:
					oap[price] += offers[offer_id][0]
			dap[offer_id] = oap

		return dap


class Pricing(object):
	def __init__(self, orders, mkt_data):
		self.orders = orders
		self.mkt_data = mkt_data

		self.utility = Utility(orders, mkt_data)
		self.market = Market(orders, mkt_data, self.utility.pos_min_util_bids_at_price(),
							 self.utility.pos_min_util_offers_at_price())

	def match_prices(self):
		prices = self.mkt_data.get_prices()
		match_prices = list()

		for price in prices:

			if self.market.avap(price) > 0:
				match_prices.append(price)

		return sorted(match_prices)

	def anchor_price(self):
		best_bid = self.mkt_data.get_best_bid()
		mid_point = self.mkt_data.get_mid_point()
		best_offer = self.mkt_data.get_best_offer()
		match_prices = self.match_prices()

		if not match_prices:
			return 0

		if mid_point in match_prices:
			anchor_price = mid_point
		elif best_bid in match_prices:
			anchor_price = best_bid
		elif best_offer in match_prices:
			anchor_price = best_offer
		else:
			mid_point_diff = dict()
			for price in match_prices:
				diff = abs(mid_point - price)
				mid_point_diff[diff] = price
			anchor_price = mid_point_diff[min(mid_point_diff)]

		return anchor_price

	def match_price(self):
		match_prices = self.match_prices()
		anchor_price = self.anchor_price()
		bids = self.orders.get_bids()
		offers = self.orders.get_offers()

		if not match_prices:
			match_price = 0

		else:
			match_price = anchor_price
			match_avap = self.market.avap(match_price)

			for bid_id in bids:
				match_alloc = self.market.bid_alloc(bid_id, match_price)
				match_eu = self.utility.bid_eu(bid_id, match_price, match_alloc)

				for price in sorted(match_prices):
					if price <= anchor_price:
						pass
					elif price > anchor_price:
						alloc = self.market.bid_alloc(bid_id, price)
						price_eu = self.utility.bid_eu(bid_id, price, alloc)
						price_avap = self.market.bid_avap(price)

						if price_eu > match_eu and price_avap > match_avap:
							match_price = price
							match_eu = price_eu
							match_avap = price_avap

			for offer_id in offers:
				match_alloc = self.market.offer_alloc(offer_id, match_price)
				match_eu = self.utility.offer_eu(offer_id, match_price, match_alloc)

				for price in sorted(match_prices, reverse= True):
					if price >= anchor_price:
						pass
					elif price < anchor_price:
						alloc = self.market.offer_alloc(offer_id, price)
						price_eu = self.utility.offer_eu(offer_id, price, alloc)
						price_avap = self.market.offer_avap(price)

						if price_eu > match_eu and price_avap > match_avap:
							match_price = price
							match_eu = price_eu
							match_avap = price_avap

		return match_price

	def get_match_volume(self):
		match_price = self.match_price()

		if match_price == 0:
			return 0
		else:
			return self.market.avap(match_price)


def test():
	mkt_data = MktData(9.9, 100000, 10.00, 100000, 0.1, 10, 1000)
	orders = Orders(mkt_data)

	orders.add_bid(9000000, 10.4, 0, 3, 200000)
	# orders.add_bid(2000000, 10.2, 0, 3, 400000)
	# orders.add_bid(3000000, 9.80, 0, 3, 900000)
	orders.add_offer(750000, 9.80, 0, 3, 100000)
	orders.add_offer(8000000, 10.4, 0, 3, 200000)
	# orders.add_offer(2000000, 9.80, 0, 3, 250000)

	utility = Utility(orders, mkt_data)
	bdap = utility.pos_min_util_bids_at_price()
	odap = utility.pos_min_util_offers_at_price()

	market = Market(orders, mkt_data, bdap, odap)

	max_dap = utility.pos_max_util_bids_at_price()

	pricing = Pricing(orders, mkt_data)

	print pricing.match_price()
	print pricing.get_match_volume()




