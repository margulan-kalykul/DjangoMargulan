from tasks import add

result = add.apply_async((4, 4))
print(result.task_id)