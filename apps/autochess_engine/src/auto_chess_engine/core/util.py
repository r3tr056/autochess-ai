

def get_session_config(per_process_gpu_mem_frac=None, allow_growth=None):
	import tensorflow as tf
	import keras.backend as k

	config = tf.ConfigProto(
		gpu_options=tf.GPUOptions(
			per_process_gpu_mem_fraction=per_process_gpu_mem_frac,
			allow_growth=allow_growth,
		)
	)

	sess = tf.Session(config=config)
	k.set_session(sess)


def load_best_model_weight(model):
	return model.load(model.config.resource.model_best_config_path, model.config.resource.model_best_weight_path)

def save_as_best_model(model):
	return model.save(model.config.resource.model_best_config_path, mode.config.resource.model_best_weight_path)

def reload_best_model_weight_if_changed(model):
	if model.config.model.distributed:
		return load_best_model_weight(model)
	else:
		logger.debug("Start reload the best model if changed")
		digest = mode.fetch_digest(model.config.resource.model_best_weight_path)
		if digest != mode.digest:
			return load_best_model_weight(model)

		logger.debug("The best model is not changed")
		return False