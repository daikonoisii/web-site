from django.contrib import admin
from .models import Information, Research, Skill, Internship, QAndA, Schedule


class InformationAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'picture')


class ResearchAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_tag', 'description', 'weight')
    ordering = ('weight',)


class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    ordering = ('-weight',)


class InternshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    ordering = ('weight',)


class QAndAAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'weight')
    ordering = ('weight',)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'month', 'weight')
    ordering = ('month', 'weight')


admin.site.register(Information, InformationAdmin)
admin.site.register(Research, ResearchAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Internship, InternshipAdmin)
admin.site.register(QAndA, QAndAAdmin)
admin.site.register(Schedule, ScheduleAdmin)
