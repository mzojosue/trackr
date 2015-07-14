import core

if __name__ == "__main__":
	core.scheduler.add_job(core.reset_db)
	core.scheduler.add_job(core.import_estimating_log)
	core.scheduler.start()
	core.app.run(host='0.0.0.0', port=8080, debug=False)