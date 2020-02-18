import pandas as pd


def data_loader_factory(observation_type):
    """
    Currently, the methods returned by this factory differ. They should not.
    TODO: Remove discrepancies between returned methods.
        See https://github.com/equinor/libres/issues/808
    """
    if observation_type == "GEN_OBS":
        return load_general_data
    elif observation_type == "SUMMARY_OBS":
        return load_summary_data
    elif observation_type == "BLOCK_OBS":
        return load_block_data
    else:
        raise TypeError("Unknown observation type: {}".format(observation_type))


def load_general_data(facade, observation_key, case_name):
    observations = facade.get_observations()
    data = pd.DataFrame()
    if observation_key not in observations:
        return data

    obs_vector = observations[observation_key]

    for time_step in obs_vector.getStepList().asList():

        node = obs_vector.getNode(time_step)
        index_list = [node.getIndex(nr) for nr in range(len(node))]

        data = (
            data.append(
                pd.DataFrame(
                    [node.get_data_points()], columns=index_list, index=["OBS"]
                )
            )
            .append(pd.DataFrame([node.get_std()], columns=index_list, index=["STD"]))
        )
    return data


def load_block_data(facade, observation_key, case_name):
    """
    load_block_data is a part of the data_loader_factory, and the other
    methods returned by this factory, require case_name, so it is accepted
    here as well.
    """
    obs_vector = facade.get_observations()[observation_key]
    loader = facade.create_plot_block_data_loader(obs_vector)

    data = pd.DataFrame()
    for report_step in obs_vector.getStepList().asList():

        obs_block = loader.getBlockObservation(report_step)

        data = (
            data.append(
                pd.DataFrame(
                    [[obs_block.getValue(i) for i in obs_block]], index=["OBS"]
                )
            )
            .append(
                pd.DataFrame([[obs_block.getStd(i) for i in obs_block]], index=["STD"])
            )
        )
    return data


def load_summary_data(facade, observation_key, case_name):
    return pd.concat(
        [
            _add_summary_observations(facade, observation_key, case_name)
        ]
    )


def _add_summary_observations(facade, data_key, case_name):
    data = facade.load_observation_data(case_name, [data_key]).transpose()
    # The index from SummaryObservationCollector is {data_key} and STD_{data_key}"
    # to match the other data types this needs to be changed to OBS and STD, hence
    # the regex.
    data = data.set_index(data.index.str.replace(r"\b" + data_key, "OBS", regex=True))
    return data.set_index(data.index.str.replace("_" + data_key, ""))
