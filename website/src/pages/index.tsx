import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="FITA - Flexible Intelligent Test Automation framework.">

      {/* Hero */}
      <section className={clsx(styles.hero, 'hero')}>
        <div className="container">
          <Heading as="h1" className="hero__title">
            {siteConfig.title}
          </Heading>
          <p className="hero__subtitle">{siteConfig.tagline}</p>

          <div className={styles.heroButtons}>
            <Link className="button button--lg button--primary" to="/fita/docs/getting-started/intro">
              Get Started
            </Link>
            <Link className="button button--secondary button--lg" to="/fita/demos">
              Explore Demos
            </Link>
          </div>
        </div>
      </section>

      <section className={styles.section}>
        <div className="container">
          <Heading as="h2">What is FITA?</Heading>
          <p className={styles.lead}>
            <span style={{ fontWeight: 600 }}>FITA</span> (Far-edge IoT device mAnagement) is a framework that <span style={{ fontWeight: 600 }}>integrates Far-edge IoT device in Kubernetes</span>, allowing them to be part of the Kubernetes orchestration and lifecycle monitoring procedures.
            <span style={{ fontWeight: 600 }}>Far-edge IoT devices</span> in the context of FITA are the <span style={{ fontWeight: 600 }}>devices equipped with sensors and actuators</span> that sense and act in the environment in which they are installed. Additionally, these devices are composed of microcontrollers, which <span style={{ fontWeight: 600 }}>do not have enough resources to run the Kubernetes Kubelet</span>.
          </p>
        </div>
      </section>

      <section className={clsx(styles.section, styles.cards)}>
        <div className="container">
          <div className="row">
            <div className="col col--4">
              <div className={styles.card}>
                <h3>Heterogeneity Management & Monitoring</h3>
                <p>
                  Automatically discover, monitor, and manage diverse Far-edge devices.
                </p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.card}>
                <h3>Dynamic Edge Workloads</h3>
                <p>
                  Dynamically deploy and reconfigure workloads on Far-edge devices using standard Kubernetes definitions, powered by flexible runtimes such as embServe.
                </p>
              </div>
            </div>
            <div className="col col--4">
              <div className={styles.card}>
                <h3>Seamless Far-Edge and Kubernetes Integration</h3>
                <p>
                  Connect Far-edge devices to Kubernetes as virtual nodes for unified orchestration.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.sectionAlt}>
      </section>

      <section className={styles.sectionCTA}>
        <div className="container text--center">
          <Heading as="h2">Ready to Try FITA?</Heading>
          <Link className="button button--primary button--lg" to="/fita/docs/getting-started/intro">
            Start with the Docs
          </Link>
        </div>
      </section>

    </Layout>
  );
}
