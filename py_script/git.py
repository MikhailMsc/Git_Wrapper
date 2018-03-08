import os
import subprocess
import platform
from functools import reduce

system = platform.system()
os_sep = os.sep
encoding = 'utf-8' if system != 'Windows' else 'cp1251'

def run_cmd(cmd, pth=None):
	output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=pth).communicate()
	output = [x.decode(encoding) for x in output]
	output = [x for x in output if x]
	if len(output) > 1: return output
	elif len(output) == 1: return output[0]

def congig(uname=None, umail=None, endstr=False):
	if uname: run_cmd('git config --global user.name ' + uname)
	if umail: run_cmd('git config --global user.email ' + umail)
	if endstr:
		run_cmd('git config --global core.autocrlf ' + 'true' if system == 'Windows' else 'input')
		run_cmd('git config --global core.safecrlf true')
	if uname is None and umail is None and endstr is False:
		output = run_cmd('git config --list')
		print(output)


class Git_Repo:
	def __init__(self, pth, clone=False, params=''):
		self.pth = os.path.normpath(pth)
		if clone:
			self.clone_rep(pth=pth, clone=clone, params=params)
		else:
			if '.git' in set(os.listdir(self.pth)):
				print(self.pth,': is repository.')
			else:
				crt = input('Directory is not repository.\nCreate repository? (y/n)\n')
				if crt == 'y':
					comand = ' '.join([x for x in ['git init', params] if x])
					output = self.run_cmd(comand)
					print(output)

	def concat_path(self,pth):
		if os_sep == '/' and '\\' in pth:
			pth = pth.replace('\\','/')
		elif os_sep == '\\' and '/' in pth:
			pth = pth.replace('/','\\')
		return os.path.join(self.pth,pth)

	def run_cmd(self,cmd, pth=''):
		if pth == '': pth = self.pth
		return run_cmd(cmd,pth)
	
	def ls(self,pth=''):
		pth = self.concat_path(pth)
		print(os.listdir(pth))

	def del_rep(self):
		output = self.run_cmd('rmdir .git' if system == 'Windows' else 'rm -rf .git')
		print(output)

	def add_file(self,pth):
		'''
		Добавление файла/изменение в файле в репозиторий перед коммитом
		'''
		#pth = self.concat_path(pth)
		#pth = pth.replace(self.pth,'').lstrip('\\').lstrip('/')
		pth = pth.strip('\\').strip('/').replace('\\','/')
		output = self.run_cmd('git add ' + pth)
		if output: print(output)

	def commit(self, comment, previous=False, params=''):
		comand = 'git commit -m "{}"'.format(comment)
		if previous: params = '--amend ' + params 
		comand = ' '.join([x for x in [comand, params] if x])
		output = self.run_cmd(comand)
		print(output)


	def status(self):
		output = self.run_cmd('git status')
		print(output)

	def history(self, logformat='--pretty=format:"%h %ad | %s%d [%an]" --graph --date=short', params='', out=True):
		'''
		--pretty="..." — определяет формат вывода.
		%h — укороченный хэш коммита
		%d — дополнения коммита («головы» веток или теги)
		%ad — дата коммита
		%s — комментарий
		%an — имя автора
		--graph — отображает дерево коммитов в виде ASCII-графика
		--date=short — сохраняет формат даты коротким и симпатичным
		'''
		comand = ' '.join([x for x in ['git log', logformat, params] if x])
		output = self.run_cmd(comand)
		if out: print(output)
		else: return output


	def goto(self, where, params='', out=True):
		comand = ' '.join([x for x in ['git checkout', params, where] if x])
		output = self.run_cmd(comand)
		if out: print(output)


	def tag(self, tag='', delete=False, goto='', params=''):
		'''
		Назначение тэга версии файла, вывод всех тегов
		-d - удалить тэг
		'''
		comand = ' '.join([x for x in ['git tag', tag, params, '-d' if delete else ''] if x])
		if comand == 'git tag': 
			output = self.run_cmd('git tag')
			if output: print(output)
		else:
			if goto:
				current_hash = self.history(logformat='--pretty=format:"%h"', dopargs='-n 1', out=False)
				self.goto(goto,out=False)

			output = self.run_cmd(comand)
			if output: print(output)
			if goto: self.goto(current_hash, out=False)


	def reset(self, commit='HEAD', file='', params=''):
		'''
		Команда reset сбрасывает буферную зону к HEAD. Это очищает буферную зону от изменений, которые мы только что проиндексировали.
		Команда reset (по умолчанию) не изменяет рабочий каталог. Поэтому рабочий каталог все еще содержит нежелательный комментарий. 
		Мы можем использовать команду goto, чтобы удалить нежелательные изменения в рабочем каталоге.

		Мы уже видели команду reset и использовали ее для согласования буферной зоны и выбранного коммита (мы использовали коммит HEAD в нашем предыдущем уроке).

		При получении ссылки на коммит (т.е. хэш, ветка или имя тега), команда reset…

		Перепишет текущую ветку, чтобы она указывала на нужный коммит
		Опционально сбросит буферную зону для соответствия с указанным коммитом
		Опционально сбросит рабочий каталог для соответствия с указанным коммитом
		'''
		if file or params:
			comand = ' '.join([x for x in ['git reset', commit, file, params] if x])
			output = self.run_cmd(comand)
			print(output)
		else:
			print('file and params is empty')


	def revert(self, params=''):
		'''
		Чтобы отменить коммит, нам необходимо сделать коммит, который удаляет изменения, сохраненные нежелательным коммитом.
		'''
		output = self.run_cmd('git revert HEAD --no-edit')
		print(output)

	def mkdir(self, dirname):
		output = self.run_cmd('mkdir ' + dirname)
		if output: print(output)

	def mv(self, what, to):
		comand = ' '.join([x for x in ['git mv', what, to]])
		output = self.run_cmd(comand)
		if output: print(output)

	def gcat_file(self, hsh, params='-t'):
		comand = ' '.join([x for x in ['git cat-file', hsh, params]])
		output = self.run_cmd(comand)
		if output: print(output)

	def cat_file(self, pth):
		comand = ' '.join([x for x in ['cat', pth]])
		output = self.run_cmd(comand)
		if output: print(output)

	def show_branch(self, branch, params=''):
		comand = ' '.join([x for x in ['git show-branch', '--list',branch,params]])
		output = self.run_cmd(comand)
		if output: print(output)

	def merge_branchs(self, branch, params=''):
		comand = ' '.join([x for x in ['git merge',branch,params]])
		output = self.run_cmd(comand)
		if output: print(output)

	def rebase_branch(self, branch, params=''):
		comand = ' '.join([x for x in ['git rebase',branch,params]])
		output = self.run_cmd(comand)
		if output: print(output)

	def clone_rep(self,pth,clone='', params=''):
		comand = ' '.join([x for x in ['git clone', clone if clone else self.pth, pth, params]])
		self.run_cmd(comand,None)
		return Git_Repo(pth)

	def remote_rep(self):
		output = self.run_cmd('git remote')
		print(output)

	def info_remote_rep(self, name='origin'):
		comand = ' '.join([x for x in ['git remote show',name]])
		output = self.run_cmd(comand)
		print(output)

	def branches(self, params=''):
		comand = ' '.join([x for x in ['git branch', params]])
		output = self.run_cmd(comand)
		print(output)

	def fetch(self, params=''):
		comand = ' '.join([x for x in ['git fetch', params]])
		output = self.run_cmd(comand)
		print(output)

	def pull(self, params=''):
		comand = ' '.join([x for x in ['git pull', params]])
		output = self.run_cmd(comand)
		print(output)

	def push(self, name, branch, params=''):
		'''
		git push origin d80e5f1:old_master # удалённо будет создана или обновлена ветка old_master. будет указывать на коммит d80e5f1
		git push origin my_local_feature:new_feature/with_nice_name   # создать или обновить ветку new_feature/with_nice_name моей my_local_feature
		git push origin :dead_feature # буквально передать "ничего" в dead_feature. Т.е. ветка dead_feature смотрит в никуда. Это удалит ветку
		'''
		comand = ' '.join([x for x in ['git push', name, branch, params]])
		output = self.run_cmd(comand)
		print(output)