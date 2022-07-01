import React, { Component } from 'react';
import EvaluationView from './evaluation/evaluation.views.js';
import './overview.style.scss';


class OverviewView extends Component {
  constructor(props) {
    super(props);
    this.props = props;
    this.state = {
      activeKey: '1',
    };
  }

  updateTab = (idx) => {
    this.setState({
      activeKey: idx,
    });
  };

  render() {
    return (
      <EvaluationView />
    );
  }
}

export default OverviewView;
