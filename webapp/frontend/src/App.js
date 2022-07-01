import React, { Component } from 'react';
import './App.scss';
import 'antd/dist/antd.css';
import 'c3/c3.min.css';
import RouteDef from './route';

class AugDesign extends Component {
  constructor(props) {
    super(props);
    this.props = props;
  }

  render() {
    return (
      <RouteDef />
    );
  }
}


export default AugDesign;
