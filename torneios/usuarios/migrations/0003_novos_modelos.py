# Generated migration file

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usuarios', '0002_inscricao'),
    ]

    operations = [
        migrations.AddField(
            model_name='torneio',
            name='status',
            field=models.CharField(
                choices=[('inscricoes', 'Inscrições'), ('chaveamento', 'Chaveamento'), ('em_progresso', 'Em Progresso'), ('finalizado', 'Finalizado')],
                default='inscricoes',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='torneio',
            name='campeao',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Equipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('jogo_principal', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('criador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Jogador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('eh_capitao', models.BooleanField(default=False)),
                ('data_entrada', models.DateTimeField(auto_now_add=True)),
                ('equipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jogadores', to='usuarios.equipe')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Confronto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fase', models.CharField(
                    choices=[('quartas', 'Quartas'), ('semifinal', 'Semifinal'), ('final', 'Final')],
                    max_length=20
                )),
                ('data_confronto', models.DateTimeField(blank=True, null=True)),
                ('realizado', models.BooleanField(default=False)),
                ('equipe1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confrontos_equipe1', to='usuarios.equipe')),
                ('equipe2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='confrontos_equipe2', to='usuarios.equipe')),
                ('vencedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='confrontos_vencidos', to='usuarios.equipe')),
                ('torneio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confrontos', to='usuarios.torneio')),
            ],
            options={
                'ordering': ['fase', 'id'],
            },
        ),
        migrations.RemoveField(
            model_name='inscricao',
            name='jogador',
        ),
        migrations.RemoveField(
            model_name='inscricao',
            name='equipe',
        ),
        migrations.AddField(
            model_name='inscricao',
            name='equipe',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='inscricoes', to='usuarios.equipe'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inscricao',
            name='confirmada',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='inscricao',
            unique_together={('equipe', 'torneio')},
        ),
    ]
