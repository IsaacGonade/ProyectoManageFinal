# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api


class task(models.Model):
    _name = "manageisaac.task"
    _description = "manageisaac.task"
    _order = "priority_order desc, end_date asc"  # Ordena por prioridad y luego por fecha de fin solo si tienen la misma prioridad

    code = fields.Char(string="Código", compute="_get_code")
    name = fields.Char(string="Nombre", readonly = False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    start_date = fields.Datetime(string="Fecha de inicio")
    end_date = fields.Datetime(string="Fecha de fin")
    is_paused = fields.Boolean(string="Pausada")
    definition_date = fields.Datetime(default=lambda p: datetime.datetime.now(), string="Fecha de definición")

    priority = fields.Selection([('low', 'Baja'),('medium', 'Media'),('high', 'Alta'),],string="Prioridad",required=True)
    priority_order = fields.Integer(string="Orden de prioridad", compute="_compute_priority_order", store=True)

    sprint_id = fields.Many2one("manageisaac.sprint", string="Sprint", required=True, ondelete="cascade")
    sprint = fields.Many2one("manageisaac.sprint", compute = "_get_sprint", store=True)
    technologies_id = fields.Many2many(comodel_name= "manageisaac.technology", relation="technologies_tareas", column1="technologies_ids", column2="tasks_ids")
    history_id = fields.Many2one("manageisaac.history", string="Historia", required=True, ondelete="cascade")
    project_id = fields.Many2one("manageisaac.project", string="Proyecto", related="history_id.project_id", ondelete="cascade", readonly=True)

    @api.depends("priority")
    def _compute_priority_order(self):
        for task in self:
            if task.priority == 'low':
                task.priority_order = 1
            elif task.priority == 'medium':
                task.priority_order = 2
            elif task.priority == 'high':
                task.priority_order = 3

    def _get_code(self):
        for task in self:
            if len(task.sprint_id) == 0:
                task.code = "TASK_"+str(task.id)
            else:
                task.code = str(task.sprint_id.name).upper()+"_"+str(task.id)

    @api.depends("code")
    def _get_sprint(self):
        for task in self:
            sprints = self.env["manageisaac.sprint"].search([("project_id.id", "=", task.history_id.project_id.id)])
            found = False
            for sprint in sprints:
                if isinstance(sprint.end_date, datetime.datetime) and sprint.end_date > datetime.datetime.now():
                    task.sprint = sprint.id
                    found = True
            if not found:
                task.sprint = False



class sprint(models.Model):
    _name = "manageisaac.sprint"
    _description = "manageisaac.sprint"

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    start_date = fields.Datetime(string="Fecha de inicio")
    end_date = fields.Datetime(string="Fecha de fin")
    duration = fields.Integer(string="Duración", default=15)

    task_id = fields.One2many(string="Tasks", comodel_name="manageisaac.task", inverse_name="sprint_id")
    project_id = fields.Many2one("manageisaac.project", string="Proyecto", required=True, ondelete="cascade")

    @api.depends("start_date", "duration")
    def _get_end_date(self):
        for sprint in self:
            if isinstance(sprint.start_date, datetime.datetime) and sprint.durantion > 0:
                sprint.end_date = sprint.start_date + datetime.timedelta(days=sprint.durantion)
            else:
                sprint.end_date = sprint.start_date



class project(models.Model):
    _name = "manageisaac.project"
    _description = "manageisaac.project"

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")

    history_id = fields.One2many(string="Historias", comodel_name="manageisaac.history", inverse_name="project_id")
    sprint_id = fields.One2many(string="Sprints", comodel_name="manageisaac.sprint", inverse_name="project_id")
    task_id = fields.One2many(string="Tareas", comodel_name="manageisaac.task", inverse_name="project_id")

class history(models.Model):
    _name = "manageisaac.history"
    _description = "manageisaac.history"

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")

    project_id = fields.Many2one("manageisaac.project", string="Proyecto", required=True, ondelete="cascade")
    task_id = fields.One2many(string="Tareas", comodel_name="manageisaac.task", inverse_name="history_id")
    used_technologies = fields.Many2many("manageisaac.technology", compute="_get_used_technologies")

    def _get_used_technologies(self):
        for history in self:
            technologies = None #Array para concatenar todas las tecnologias
            for task in history.task_id: #para cada una de las tareas de la historia
                if not technologies:
                    technologies = task.technologies_id
                else:
                    technologies = technologies + task.technologies_id
            history.used_technologies = technologies #Asignar las tecnologias a la historia

class technology(models.Model):
    _name = "manageisaac.technology"
    _description = "manageisaac.technology"

    name = fields.Char(string="Nombre", readonly=False, required=True, help="Introduzca el nombre")
    description = fields.Text(string="Descripción")
    photo = fields.Image(string="Imagen")

    tasks_id = fields.Many2many(comodel_name= "manageisaac.task", relation="technologies_tareas", column1="tasks_ids", column2="technologies_ids")
    #developer_id = fields.Many2many(comodel_name="manageisaac.developer", relation="developer_technologies", column1="technologies_id", column2="developer_id")

class developer(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    is_dev = fields.Boolean()

    technologies = fields.Many2many("manageisaac.technology", relation="developer_technologies", column1="developer_id", column2="technologies_id")


