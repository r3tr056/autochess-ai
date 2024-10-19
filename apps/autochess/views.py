
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

class ProfileView(LoginRequiredMixin, TemplateView):
	template_name = 'templates/profile.html'

	def get_context_data(self, *args, **kwargs):
		context = super(ProfileView, self).get_context_data(**kwargs)
		user_utils.add_generic_context(context, request=self.request)
		user_utils.add_theme_list(context)

		target_user_id = kwargs['pk']
		target_user = User.objects.filter(id=target_user_id).first()
		if not target_user:
			return False
		context['target_user'] = target_user

		# performances
		perfs = dict()
		user_ranking = UserRanking.objects.get_or_create(user=self.request.user)[0]
		user_elo = user_ranking.get_elo('chess')
		if user_elo:
			perfs['elo'] = user_elo
			perfs['level'] = user_ranking.get_user_level('chess')

		context['performances'] = perfs
		parsed_perf_data = RankingUtils().parse_history_data('chess', target_user)
		context['performances_parsed'] = parsed_perf_data

		# search user games
		context['player_history'] = ProfileLoadData().get_player_history(target_user_id)

		user_colorset = UserColorSet.objects.filter(user=target_user).first()
		if not user_colorset:
			user_colorset = UserColorSet(user=target_user)
			default_colorset = ChessBoard.BoardColorSet().get_default_colorset()
			user_colorset.set_data('chess', default_colorset)
		context['user_customization'] = user_colorset.get_data('')

		return { 'context': context }

	def get(self, *args, **kwargs):
		context = self.get_context_data(*args, **kwargs)
		if not context:
			return HttpResponseRedirect(reverse('login'))
		return super(ProfileView, self).get(*args, **kwargs)

