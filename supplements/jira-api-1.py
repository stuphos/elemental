# https://docs.atlassian.com
# software/jira/docs/api/REST/7.6.1/
# #api/2/customFieldOption-getCustomFieldOption

def methodElementsOf(r):
	return r.find('div', attrs = {'class': 'methods'}) \
		.findAll('div', attrs = {'class': 'method'})

def methodsOf(r):
	for m in methodElementsOf(r):
		m = m.find('h4')

		(method, url, *args) = m.find('code').text.split('\xa0')

		url = [[True, name[1:-1]] if (name[:1] == '{' and name[-1:] == '}')
			   else [False, name] for name in url.split('/')]

		yield [method, url,
			   m.find('span').find('a').text] + args

def resourceOf(r):
	return (r.find('h3')['id'],
		    list(methodsOf(r)))


def pageOf(page):
	return map(resourceOf, page.findAll
		('div', attrs = {'class': 'resource'}))


def string_methodsOf(page):
	from bs4 import BeautifulSoup as bs4
	return pageOf(bs4(page)) # loadable(page).loading.soup)


class jiraApi(dict):
	def __init__(self, api):
		# import pdb; pdb.set_trace()
		dict.__init__(self, ((apiId, self.resource
			(self, apiId, methods)) for
				(apiId, methods) in api))


	def requestCall(self, host, argv, *args, **kwdCall):
		'''
		api.requestCall \
			(https['docs.atlassian.com'],
			 'api/2/dashboard "Get dashboard" --id=x')

		'''

		if isinstance(argv, str):
			from shlex import split
			argv = split(argv)


		(method, index, *argv) = argv
		kwd = dict()

		for a in argv:
			if a.startswith('--'):
				a = a[2:]
				i = a.find('=')

				kwd[a[:i]] = a[i+1:]


		for method in api[method]:
			if method.caption == index:
				return method.requestCall \
					(host, *args, **dict
						(kwdCall, **kwd))

		# return api[method][int(index)] \
		# 	.requestCall(host, **dict
		#		(kwdCall, **kwd))


	class resource(list):
		def __init__(self, api, apiId, methods):
			list.__init__(self, (self.method(self, *m) for m in methods))

			self.api = api
			self.apiId = apiId


		def build(self, method, lead, **kwd):
			method = list(method.build(**kwd))

			if method[:len(lead)] == lead:
				leadVal = method[:len(lead)]
				method = method[len(lead):]
			else:
				leadVal = []

			apiId = self.apiId.split('/')
			if method[:len(apiId)] == apiId:
				apiVal = method[:len(apiId)]
				method = method[len(apiId):]
			else:
				apiVal = []

			return [leadVal, apiVal, method]


		class method(list):
			def __init__(self, resource, method, url, caption):
				# import pdb; pdb.set_trace()
				# list.__init__(self, (self.variable(self, u) if var
				# 	else self.path(self, u) for (var, u) in url))

				list.__init__(self, (self.variable(u) if var
					else self.path(u) for (var, u) in url))

				self.resource = resource
				self.method = method
				self.caption = caption

			class url(str):
				# def __init__(self, method, value):
				# 	str.__init__(self, value)

				# 	self.method = method

				variable = False
				path = False

			class variable(url):
				variable = True
			class path(url):
				path = True


			def build(self, **kwd):
				for u in self:
					yield kwd[str(u)] if \
						u.variable else \
							str(u)

			def buildArgs(self, lead, **kwd):
				return self.resource.build \
					(self, lead, **kwd)


			def call(self, **kwd):
				return [self.method, '/'.join
						(self.build(**kwd))]


			methodNames = dict \
				(GET = 'get',
				 POST = 'post')

			def request(self, host, **kwd):
				(method, path) = self.call(**kwd)

				return getattr(host[path],
						self.methodNames
							[method])

			def requestCall(self, host, *args, **kwd):
				return self.request \
					(host, **kwd) \
						(*args)


if __name__ == '__main__':
	from sys import argv, stdout
	import json

	for a in argv[1:]:
		if a.endswith('.json'):
			api = jiraApi(json.load(open(a)))

		else: # if a.endswith('.html'):
			json.dump(list(string_methodsOf
				(open(a).read())), stdout,
				indent = 1)


'''
<div class="resource">
	<h3 id="api/2/customFieldOption">
		<a href="#api/2/customFieldOption">api/2/customFieldOption</a>
		<a class="expand-methods">Expand all methods</a>
	</h3>
	<div class="methods">
		<div class="method">
			<h4 id="api/2/customFieldOption-getCustomFieldOption" class="expandable">
				<span class="left"><button class="expand"></button>
					<a href="#api/2/customFieldOption-getCustomFieldOption">Get custom field option</a>
				</span>
				<code>GET&nbsp;/rest/api/2/customFieldOption/{id}</code>
			</h4>

'''
